import re
import json
import time
import uuid
import asyncio
from datetime import datetime
from typing import Dict, Tuple
from openai import AsyncOpenAI
from deepseek_api.tool import AcademicQueryTools

def is_in_time_range():
    now = datetime.now()
    h, m = now.hour, now.minute
    return (0 <= h < 8) or (h == 0 and m >= 30) or (h == 8 and m <= 30)


class MetricsCollector:
    def __init__(self):
        self.cache_stats = {"hit_tokens": 0, "miss_tokens": 0}
        self.session_stats = {"total_created": 0, "active_sessions": 0, "total_duration": 0.0}
        self.api_usage = {"total_tokens": 0, "total_cost": 0.0}
        self.last_cost = 0.0

    def record_cache(self, hit_tokens, miss_tokens):
        self.cache_stats["hit_tokens"] += hit_tokens
        self.cache_stats["miss_tokens"] += miss_tokens

    def record_session_start(self):
        self.session_stats["total_created"] += 1
        self.session_stats["active_sessions"] += 1

    def record_session_end(self, duration):
        self.session_stats["active_sessions"] -= 1
        self.session_stats["total_duration"] += duration

    def record_api_usage(self, usage):
        self.api_usage["total_tokens"] += usage.get("total_tokens", 0)
        cost = sum((usage.get("hit_tokens", 0) * 0.5 / 1e6, usage.get("miss_tokens", 0) * 2 / 1e6,
                    usage.get("return_tokens", 0) * 8 / 1e6)) * (0.5 if is_in_time_range() else 1)
        self.api_usage["total_cost"] += cost
        self.last_cost = cost
        return cost

    def get_last_cost(self):
        return self.last_cost


class ServiceSession:
    def __init__(self, service_id, service_key, user_info, user_state):
        self.service_id = service_id
        self.service_key = service_key
        self.user_info = user_info
        self.user_state = user_state
        self.created_time = time.time()
        self.last_active = self.created_time
        self.message_count = 0
        self.messages = self._init_system_message()

    def _init_system_message(self):
        """保持原有数据结构不变"""
        Service = {
            "WUT": "为已认证用户提供简单的个人信息查询服务，以及基础知识的问答，" +
                   "可查询的信息包括: 课程信息，考试安排，考试成绩，期末总评，这四个方面。" +
                   "回答应该简短并且礼貌，执行查询服务时，从用户的信息中理解用户的需求。" +
                   "务必做到准确不能有不实信息，尤其注意日期时间相关，对输出进行检查。" +
                   "没查询到完美符合要求的信息就对用户回复没有，不要编造信息",
            "BOT": "陪用户闲聊，依照用户需求进行互动，回答应该简短并且礼貌",
            "ETO": "尽可能帮助用户解决问题，做到详细清晰"
        }

        return [{"role": "system",  "content": "你给出的任何回答必须基于以下信息: " +
                 f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}" +
                 f"你的身份: 由 'Dr.ETO' 搭建的 'deepseek v3' 语言模型接口" +
                 f"交流语言: 默认中文，如果用户有特殊要求，可以依照需求" +
                 f"你的工作: {Service[self.service_key]}" +
                 f"用户状态: {self.user_state}" +
                 f"用户信息: {self.user_info}"}]


class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, ServiceSession] = {}
        self.user_session_map: Dict[Tuple[str, str], str] = {}  # (user_info, service_key) -> service_id
        self.lock = asyncio.Lock()
        self.metrics = MetricsCollector()

    async def get_session(self, service_key, user_info, user_state) -> ServiceSession:
        async with self.lock:
            # 检查已认证用户是否已有会话
            if user_state == "已认证":
                session_key = (user_info, service_key)
                if session_key in self.user_session_map:
                    existing_id = self.user_session_map[session_key]
                    if existing_id in self.sessions:
                        return self.sessions[existing_id]

            # 创建新会话
            new_id = str(uuid.uuid4())
            new_session = ServiceSession(service_id=new_id, service_key=service_key, user_info=user_info, user_state=user_state)

            self.sessions[new_id] = new_session
            self.metrics.record_session_start()

            # 记录已认证用户的映射
            if user_state == "已认证":
                self.user_session_map[(user_info, service_key)] = new_id

            return new_session

    async def _remove_session(self, service_id):
        if service_id in self.sessions:
            session = self.sessions[service_id]
            # 更新指标
            duration = time.time() - session.created_time
            self.metrics.record_session_end(duration)

            # 清理用户映射
            if session.user_state == "已认证":
                session_key = (session.user_info, session.service_key)
                if self.user_session_map.get(session_key) == service_id:
                    del self.user_session_map[session_key]

            del self.sessions[service_id]


def sanitize_parameters(params):
    """参数消毒处理"""
    sanitized = {}

    # 处理查询类型
    if "query_type" in params:
        sanitized["query_type"] = str(params["query_type"]).lower()
        if sanitized["query_type"] not in ["course", "exam", "grade", "evaluates"]:
            raise ValueError("无效查询类型")

    # 处理天数参数
    if "days" in params:
        try:
            days = int(params["days"])
            sanitized["days"] = max(1, min(30, days))
        except:
            sanitized["days"] = 7

    # 处理关键词（防注入处理）
    if "keyword" in params:
        sanitized["keyword"] = re.sub(r"[^\w\u4e00-\u9fa5]", "", str(params["keyword"]))[:50]

    return sanitized


class AsyncDeepSeekClient:
    def __init__(self, api_key, metrics: MetricsCollector):
        self.client = AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        self.query_tools = AcademicQueryTools()
        self.metrics = metrics
        self.tools = [{
            "type": "function",
            "function": {
                "name": "query_academic_info",
                "description": "学术信息查询（课程/考试/成绩/总评）",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query_type": {
                            "type": "string",
                            "enum": ["course", "exam", "grade", "evaluates"],
                            "description": "查询类型"
                        },
                        "days": {
                            "type": "integer",
                            "description": "查询天数（仅课程查询需要）"
                        },
                        "exam_type": {
                            "type": "string",
                            "description": "考试类型（仅考试查询需要）"
                        }
                    },
                    "required": ["query_type"]
                }
            }
        }]

    async def process_message(self, session: ServiceSession, user_input):
        session.messages.append({"role": "user", "content": user_input})
        session.message_count += 1
        current_cost = 0.0

        try:
            response = await self.client.chat.completions.create(
                model="deepseek-chat",
                messages=session.messages,
                tools=self.tools,
                temperature=0.7,
                max_tokens=4096,
            )

            # 记录API使用指标
            if hasattr(response, "usage"):
                usage_data = {
                    "total_tokens": response.usage.total_tokens,
                    "hit_tokens": getattr(response.usage, "prompt_cache_hit_tokens", 0),
                    "miss_tokens": getattr(response.usage, "prompt_cache_miss_tokens", 0)
                }
                usage_data["return_tokens"] = usage_data["total_tokens"] - usage_data["hit_tokens"] - usage_data["miss_tokens"]
                current_cost = self.metrics.record_api_usage(usage_data)
                self.metrics.record_cache(usage_data["hit_tokens"], usage_data["miss_tokens"])

            message = response.choices[0].message
            if message.tool_calls:
                return await self.handle_tool_call(session, message)

            session.messages.append({"role": "assistant", "content": message.content})
            session.message_count += 1

            return {"service_id": session.service_id, "response": message.content, "tools": None, "cost": current_cost}

        except Exception as e:
            error_cost = current_cost if current_cost else 0.0
            return {"service_id": session.service_id, "response": f"请求失败：{str(e)}", "tools": None, "cost": error_cost}

    async def handle_tool_call(self, session: ServiceSession, message):
        tool_call = message.tool_calls[0]
        session.messages.append(message)

        try:
            # 解析参数并获取用户信息
            arguments = sanitize_parameters(json.loads(tool_call.function.arguments))
            query_type = arguments.get("query_type", "")
            user_info = session.user_info  # 从会话获取用户信息

            # 根据查询类型分发请求
            query_methods = {
                "course": (self.query_tools.query_courses, ["days", "keyword"]),
                "exam": (self.query_tools.query_exams, ["exam_type", "keyword"]),
                "grade": (self.query_tools.query_grades, ["keyword"]),
                "evaluates": (self.query_tools.query_evaluates, ["keyword"])
            }

            if query_type not in query_methods:
                raise ValueError("无效的查询类型")

            method, params = query_methods[query_type]
            query_args = {"user_info": user_info}

            # 动态构建参数
            for p in params:
                if p in arguments:
                    query_args[p] = arguments[p]

            # 执行实时查询（每次都会新建数据管理器）
            result = await method(**query_args)

        except json.JSONDecodeError as e:
            result = {"status": "error", "message": f"参数解析失败: {str(e)}"}
        except Exception as e:
            result = {"status": "error", "message": f"查询失败: {str(e)}"}

        tool_response = json.dumps(result, ensure_ascii=False)  # 构造工具响应
        session.messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": tool_response})
        return await self.process_message(session, "")  # 继续处理后续对话


class ChatSystem:
    def __init__(self, api_key):
        self.session_manager = SessionManager()
        self.client = AsyncDeepSeekClient(api_key, self.session_manager.metrics)

        self.lock = asyncio.Lock()  # 文件操作锁
        self.filename = "database/*****/dialogues.json"  # 新增文件名属性

    async def handle_request(self, service_key, user_info, user_state, user_input):
        print(f"Ask: {user_input}")
        start_time = time.time()
        session = await self.session_manager.get_session(service_key, user_info, user_state)
        result = await self.client.process_message(session, user_input)
        duration = f"{round(time.time() - start_time, 2):.2f}s"  # 计算持续时间

        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        service_id = session.service_id

        # 确保文件操作原子性
        async with self.lock:
            try:  # 读取现有数据或初始化
                with open(self.filename.replace("*****", user_info), 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception as e:
                print(f"读取文件失败: {str(e)}")
                data = {"authenticate": False, "password": "", "last_time": "", "service": {}}

            # 确保 service_id 存在于 data["service"] 中
            if service_id not in data["service"]:
                data["service"][service_id] = {
                    "service": service_key,
                    "last_time": current_time,
                    "dialogues": []
                }

            current_cost = self.session_manager.metrics.get_last_cost()
            data["service"][service_id]["dialogues"].append({
                "ask": user_input,
                "ans": result['response'],
                "time": current_time,
                "duration": duration,
                "cost": f"{round(current_cost, 6):.6f}"
            })

            try:  # 保存更新
                with open(self.filename.replace("*****", user_info), 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"保存文件失败: {str(e)}")

        session.last_active = time.time()
        print(f"Ans: {result['response']}\n" + "-" * 100)
        return {"service_id": result["service_id"], "response": result["response"], "needs_action": result["tools"] is not None}

    def get_metrics(self):
        return {"cache": self.session_manager.metrics.cache_stats,
                "sessions": self.session_manager.metrics.session_stats,
                "api_usage": self.session_manager.metrics.api_usage}


async def main():
    api_key = "sk-*****"
    chat_system = ChatSystem(api_key)

    # await chat_system.handle_request(
    #     service_key="WUT",
    #     user_info="1024005786",
    #     user_state="已认证",
    #     user_input="你能提供什么帮助"
    # )

    await chat_system.handle_request(
        service_key="WUT",
        user_info="1024005786",
        user_state="已认证",
        user_input="明天有什么课"
    )

    # await chat_system.handle_request(
    #     service_key="WUT",
    #     user_info="1024005786",
    #     user_state="已认证",
    #     user_input="我本学期选修了哪些科目"
    # )

    # await chat_system.handle_request(
    #     service_key="BOT",
    #     user_info="1024005786",
    #     user_state="已认证",
    #     user_input="请你扮演一只猫娘进行一些问候"
    # )

    print(f"\n又亏了这么多钱: {chat_system.get_metrics()['api_usage']['total_cost']}")


if __name__ == "__main__":
    asyncio.run(main())
