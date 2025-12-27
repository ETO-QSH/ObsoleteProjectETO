from entrance import ChatSystem
from login import login_and_fetch
from crypto import CryptoManager, KeyManager, MigrationKeyManager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Dict, Optional
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path
import asyncio
import json


key_manager = KeyManager()  # 初始化密钥管理器
crypto = CryptoManager(key_manager)  # 初始化加密管理器
app = FastAPI(title="WUT-ETO DeepSeek API Service")  # 初始化FastAPI应用

# 全局配置
DATA_DIR = Path("database")
DATA_DIR.mkdir(parents=True, exist_ok=True)
file_lock = asyncio.Lock()  # 异步文件锁

# 初始化聊天系统
with open("config/keys.json", "r") as f:
    chat_system = ChatSystem(api_key=json.load(f).get("api_key", None))  # 初始化聊天系统，同时避免api_key暴露


class ServerConfig(BaseModel):
    api_key: str
    rotate_days: int = 30


class LoginRequest(BaseModel):
    username: str
    password: str = None


class ChatRequest(BaseModel):
    service_key: str
    user_input: str
    session_id: Optional[str] = None


def get_user_file(username):
    """获取用户数据文件路径"""
    user_dir = DATA_DIR / username
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir / "dialogues.json"


async def load_user_data(username):
    """异步加载用户数据"""
    async with file_lock:
        user_file = get_user_file(username)
        try:
            with open(user_file, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="用户不存在")
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="用户数据损坏")


async def save_user_data(username, data):
    """异步保存用户数据"""
    async with file_lock:
        user_file = get_user_file(username)
        with open(user_file, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)


@app.on_event("startup")
async def initialize_system():
    """触发密钥轮换"""
    global crypto  # 加载历史密钥用于解密旧数据

    try:
        if not key_manager.current_key:
            key_manager.rotate_key()
        crypto = CryptoManager(key_manager)
    except Exception as e:
        raise RuntimeError(f"系统初始化失败: {str(e)}")


@app.on_event("startup")
async def rotate_keys():
    """增强的密钥轮换逻辑"""
    try:
        old_key = key_manager.current_key
        new_key = key_manager.rotate_key()

        # 执行数据迁移
        old_crypto = CryptoManager(MigrationKeyManager(old_key))
        new_crypto = CryptoManager(MigrationKeyManager(new_key))
        CryptoManager.migrate_data(old_crypto, new_crypto, str(DATA_DIR))

        return {"status": "success", "new_key": key_manager.get_key_fingerprint(new_key)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/login", summary="用户登录")
async def api_login(request: LoginRequest, background_tasks: BackgroundTasks):
    """处理用户登录请求"""
    if not request.password:
        user_data = await load_user_data(request.username)
        stored_password = user_data.get("password", "")  # 使用存储的密码
        if not stored_password:
            raise HTTPException(status_code=400, detail="密码丢失，请重新登陆！")
        request.password = crypto.decrypt_password(stored_password)  # 使用密钥管理器解密

    # 发送登录请求
    login_result = await login_and_fetch(request.username, request.password)
    if login_result["status"] != "success":
        raise HTTPException(status_code=401, detail=login_result.get("message", "登录失败"))

    # 加密存储时使用最新密钥
    encrypted_password = crypto.encrypt_password(request.password)
    user_data = {"authenticate": True, "password": encrypted_password, "last_time": datetime.now().isoformat(), "service": {}}

    background_tasks.add_task(save_user_data, request.username, user_data)  # 后台保存数据
    return JSONResponse(content={"status": "success", "message": "登录成功", "data": ""})


@app.post("/refresh/{username}", summary="刷新用户数据")
async def refresh_data(username, background_tasks: BackgroundTasks):
    """刷新用户教务数据"""
    user_data = await load_user_data(username)
    password = user_data.get("password", "")  # 使用存储的密码

    if not password:
        raise HTTPException(status_code=400, detail="密码丢失，请重新登陆！")

    login_result = await login_and_fetch(username, crypto.decrypt_password(password))

    if login_result["status"] != "success":
        raise HTTPException(status_code=401, detail=login_result.get("message", "登录失败，请重新登陆！"))

    # 在后台执行数据刷新
    background_tasks.add_task(login_and_fetch, username, password)
    return {"status": "success", "message": "数据刷新已开始"}


@app.post("/chat/{username}", summary="处理对话请求")
async def handle_chat_request(username, request: ChatRequest, background_tasks: BackgroundTasks):
    """处理聊天请求"""
    user_data = await load_user_data(username)  # 加载用户数据

    # 检查认证状态
    if not user_data.get("authenticate", False):
        raise HTTPException(status_code=403, detail="用户未认证")

    # 处理聊天请求
    try:
        chat_result = await chat_system.handle_request(
            service_key=request.service_key,
            user_info=username,
            user_state="已认证",
            user_input=request.user_input
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 构造响应数据
    response_data = {
        "service_id": chat_result["service_id"],
        "response": chat_result["response"],
        "needs_action": chat_result["needs_action"],
        "metrics": chat_system.get_metrics()
    }

    background_tasks.add_task(save_chat_record, username, request, chat_result)  # 在后台保存对话记录
    return JSONResponse(content=jsonable_encoder(response_data))


async def save_chat_record(username, request: ChatRequest, chat_result: Dict):
    """异步保存聊天记录"""
    current_time = datetime.now().isoformat()
    user_data = await load_user_data(username)

    session_id = chat_result["service_id"]
    service_key = request.service_key

    # 更新会话记录
    user_data["service"].setdefault(session_id, {
        "service": service_key,
        "last_time": current_time,
        "dialogues": []
    })

    user_data["last_time"] = current_time  # 更新最后活跃时间
    await save_user_data(username, user_data)


@app.get("/health", summary="健康检查")
async def health_check():
    """服务健康检查端点"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
