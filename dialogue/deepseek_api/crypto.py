import os
import json
import base64
import logging
from pathlib import Path
from tempfile import TemporaryDirectory
from datetime import datetime, timedelta

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KeyManager:
    """增强型密钥管理类"""
    def __init__(self, key_file="config/keys.json"):
        self.key_file = Path(key_file)
        self.key_file.parent.mkdir(exist_ok=True, parents=True)
        self.api_key = None
        self.encryption_keys = []
        self._load_keys()

        # 自动生成初始密钥
        if not self.current_key_obj:
            logger.warning("No active key found, generating initial key...")
            self.rotate_key()

    def _load_keys(self):
        """安全加载密钥文件"""
        if self.key_file.exists():
            try:
                with open(self.key_file, "r") as f:
                    data = json.load(f)
                    self.api_key = data.get("api_key")
                    self.encryption_keys = data.get("encryption_keys", [])

                    # 转换旧格式
                    if isinstance(self.encryption_keys, list) and len(self.encryption_keys) > 0 and isinstance(self.encryption_keys[0], str):
                        self.encryption_keys = [{"key": k, "created": datetime.now().isoformat(), "active": False} for k in self.encryption_keys]
                        self.encryption_keys[0]["active"] = True

            except Exception as e:
                logger.error(f"加载密钥文件失败: {str(e)}")
                raise

    def _save_keys(self):
        """安全保存密钥文件"""
        try:
            with open(self.key_file, "w") as f:
                json.dump({"api_key": self.api_key, "encryption_keys": [{"key": k["key"], "created": k["created"], "active": k["active"]}
                    for k in self.encryption_keys if datetime.fromisoformat(k["created"]) > datetime.now() - timedelta(days=90)]}, f, indent=2, ensure_ascii=False)
                os.chmod(self.key_file, 0o600)  # 设置文件权限

        except Exception as e:
            logger.error(f"保存密钥文件失败: {str(e)}")
            raise

    @property
    def current_key_obj(self):
        """获取当前激活的密钥对象"""
        active_keys = [k for k in self.encryption_keys if k.get("active")]
        return active_keys[0] if active_keys else None

    @property
    def current_key(self):
        """获取当前激活的密钥值"""
        key_obj = self.current_key_obj
        return key_obj["key"] if key_obj else None

    def rotate_key(self):
        """安全轮换密钥"""
        try:
            # 生成新密钥
            new_key = Fernet.generate_key().decode()
            new_key_record = {"key": new_key, "created": datetime.now().isoformat(), "active": True}

            # 停用旧密钥
            for key in self.encryption_keys:
                key["active"] = False

            # 添加新密钥
            self.encryption_keys.insert(0, new_key_record)

            # 清理过期密钥（保留最近30天）
            self.encryption_keys = [k for k in self.encryption_keys if datetime.fromisoformat(k["created"]) > datetime.now() - timedelta(days=30)]

            self._save_keys()
            logger.info(f"密钥轮换成功，新密钥ID: {self.get_key_fingerprint(new_key)}")
            return new_key

        except Exception as e:
            logger.critical(f"密钥轮换失败: {str(e)}")
            raise

    @staticmethod
    def get_key_fingerprint(key):
        """生成密钥指纹"""
        digest = hashes.Hash(hashes.SHA256())
        digest.update(key.encode())
        return base64.b64encode(digest.finalize()).decode()[:16]


class CryptoManager:
    """增强型加密管理类"""
    def __init__(self, key_manager: KeyManager):
        self.key_manager = key_manager

    def encrypt_password(self, plain_password):
        """安全加密方法"""
        current_key = self.key_manager.current_key
        if not current_key:
            raise ValueError("没有可用的激活密钥")

        try:
            # 密钥派生
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)
            derived_key = base64.urlsafe_b64encode(kdf.derive(current_key.encode()))

            # 加密数据
            fernet = Fernet(derived_key)
            cipher_text = fernet.encrypt(plain_password.encode())
            return f"{base64.urlsafe_b64encode(salt).decode()}${cipher_text.decode()}"  # 返回组合字符串

        except Exception as e:
            logger.error(f"加密失败: {str(e)}")
            raise

    def decrypt_password(self, encrypted_password):
        """安全解密方法"""
        current_key = self.key_manager.current_key
        if not current_key:
            raise ValueError("没有可用的激活密钥")

        try:
            # 解析加密字符串
            salt_b64, cipher_text = encrypted_password.split("$", 1)
            salt = base64.urlsafe_b64decode(salt_b64)
        except ValueError:
            raise ValueError("无效的加密格式")
        except Exception as e:
            raise ValueError(f"解析失败: {str(e)}")

        try:
            # 密钥派生
            kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)
            derived_key = base64.urlsafe_b64encode(kdf.derive(current_key.encode()))

            # 解密数据
            fernet = Fernet(derived_key)
            return fernet.decrypt(cipher_text.encode()).decode()

        except Exception as e:
            logger.error(f"解密失败 | 当前密钥指纹: {KeyManager.get_key_fingerprint(current_key)}")
            raise ValueError(f"解密失败：密钥可能已轮换。{e}")

    @classmethod
    def migrate_data(cls, old_crypto, new_crypto, data_dir="database"):
        """安全数据迁移方法"""
        logger.info("开始数据迁移...")
        migration_report = {"total": 0, "success": 0, "failures": []}

        for user_file in Path(data_dir).rglob("*/dialogues.json"):
            migration_report["total"] += 1
            try:
                with open(user_file, "r+", encoding="utf-8") as f:
                    # 读取并验证数据
                    data = json.load(f)
                    if "password" not in data or not data["password"]:
                        continue

                    # 解密旧数据
                    try:
                        decrypted = old_crypto.decrypt_password(data["password"])
                    except Exception as e:
                        raise ValueError(f"解密失败: {str(e)}")

                    # 加密新数据
                    try:
                        new_encrypted = new_crypto.encrypt_password(decrypted)
                    except Exception as e:
                        raise ValueError(f"加密失败: {str(e)}")

                    # 更新数据
                    data["password"] = new_encrypted
                    f.seek(0)
                    json.dump(data, f, ensure_ascii=False, indent=2)
                    f.truncate()

                migration_report["success"] += 1
                logger.debug(f"成功迁移: {user_file}")

            except Exception as e:
                error_msg = f"{user_file}: {str(e)}"
                migration_report["failures"].append(error_msg)
                logger.error(error_msg)

        logger.info(f"迁移完成 | 总数: {migration_report['total']} | 成功: {migration_report['success']} | 失败: {len(migration_report['failures'])}")
        return migration_report


class MigrationKeyManager:
    """数据迁移专用密钥管理器"""
    def __init__(self, fixed_key):
        self.fixed_key = fixed_key

    @property
    def current_key(self):
        return self.fixed_key

    @property
    def encryption_keys(self):
        return [{"key": self.fixed_key, "created": datetime.now().isoformat(), "active": True}]


if __name__ == "__main__":
    # 创建临时测试环境
    with TemporaryDirectory() as temp_dir:
        print(f"【创建测试环境】临时目录: {temp_dir}")

        # 初始化目录结构
        test_db_dir = Path(temp_dir) / "database"
        test_db_dir.mkdir(parents=True, exist_ok=True)
        test_config_dir = Path(temp_dir) / "config"
        test_config_dir.mkdir(parents=True, exist_ok=True)

        # 初始化密钥文件路径
        test_keys_file = test_config_dir / "keys.json"

        # 重写KeyManager使用测试路径
        class TestKeyManager(KeyManager):
            def __init__(self):
                super().__init__(key_file=str(test_keys_file))

        # ========== 第一阶段：初始设置 ==========
        print("\n=== 阶段1：系统初始化 ===")

        # 初始化密钥系统
        km = TestKeyManager()
        crypto = CryptoManager(km)
        print(f"初始密钥指纹: {km.get_key_fingerprint(km.current_key)}")

        # 创建初始测试用户
        test_users = [{"username": "user1", "password": "P@ssw0rd1!"}]

        # 保存初始用户数据
        def save_user(user):
            user_dir = test_db_dir / user["username"]
            # 修复点：添加 parents=True
            user_dir.mkdir(parents=True, exist_ok=True)  # 递归创建目录
            user_file = user_dir / "dialogues.json"
            encrypted = crypto.encrypt_password(user["password"])
            with open(user_file, "w") as f:
                json.dump({"password": encrypted, "create_time": datetime.now().isoformat()}, f, indent=2)
            return encrypted

        print("\n【创建初始用户】")
        user1_encrypted = save_user(test_users[0])
        print(f"user1 加密结果: {user1_encrypted[:30]}...")

        # ========== 第二阶段：初始验证 ==========
        print("\n=== 阶段2：初始验证 ===")

        def verify_decryption(username, expected_pass):
            user_file = test_db_dir / username / "dialogues.json"
            with open(user_file) as f:
                encrypted = json.load(f)["password"]
            try:
                decrypted = crypto.decrypt_password(encrypted)
                status = "✅" if decrypted == expected_pass else "❌"
                print(f"{status} {username}: 预期 '{expected_pass}' | 实际 '{decrypted}'")
            except Exception as e:
                print(f"❌ {username} 解密失败: {str(e)}")

        print("初始解密验证:")
        verify_decryption("user1", "P@ssw0rd1!")

        # ========== 第三阶段：第一次密钥轮换和迁移 ==========
        print("\n=== 阶段3：第一次密钥轮换 ===")

        # 记录旧密钥
        key_before_rotate1 = km.current_key
        print(f"当前密钥指纹: {km.get_key_fingerprint(key_before_rotate1)}")

        # 执行密钥轮换
        new_key1 = km.rotate_key()
        print(f"新密钥指纹: {km.get_key_fingerprint(new_key1)}")

        # 创建迁移工具
        old_crypto1 = CryptoManager(MigrationKeyManager(key_before_rotate1))
        new_crypto1 = CryptoManager(km)

        # 执行第一次迁移
        print("\n【第一次数据迁移】")
        report1 = CryptoManager.migrate_data(old_crypto1, new_crypto1, str(test_db_dir))
        print(f"迁移报告: 成功 {report1['success']}/总数 {report1['total']}")

        # 添加第二个用户（使用新密钥）
        print("\n【添加新用户】")
        test_users.append({"username": "user2", "password": "P@ssw0rd2!"})
        user2_encrypted = save_user(test_users[1])
        print(f"user2 加密结果: {user2_encrypted[:30]}...")

        # ========== 第四阶段：第一次迁移后验证 ==========
        print("\n=== 阶段4：第一次迁移后验证 ===")

        print("当前使用的密钥指纹:", km.get_key_fingerprint(km.current_key))
        print("解密验证:")
        verify_decryption("user1", "P@ssw0rd1!")  # 迁移后的用户
        verify_decryption("user2", "P@ssw0rd2!")  # 新增用户

        # ========== 第五阶段：第二次密钥轮换和迁移 ==========
        print("\n=== 阶段5：第二次密钥轮换 ===")

        # 记录旧密钥
        key_before_rotate2 = km.current_key
        print(f"当前密钥指纹: {km.get_key_fingerprint(key_before_rotate2)}")

        # 执行第二次密钥轮换
        new_key2 = km.rotate_key()
        print(f"新密钥指纹: {km.get_key_fingerprint(new_key2)}")

        # 创建迁移工具
        old_crypto2 = CryptoManager(MigrationKeyManager(key_before_rotate2))
        new_crypto2 = CryptoManager(km)

        # 执行第二次迁移
        print("\n【第二次数据迁移】")
        report2 = CryptoManager.migrate_data(old_crypto2, new_crypto2, str(test_db_dir))
        print(f"迁移报告: 成功 {report2['success']}/总数 {report2['total']}")

        # ========== 第六阶段：最终验证 ==========
        print("\n=== 阶段6：最终验证 ===")

        print("当前使用的密钥指纹:", km.get_key_fingerprint(km.current_key))
        print("最终解密验证:")
        verify_decryption("user1", "P@ssw0rd1!")  # 两次迁移后的用户
        verify_decryption("user2", "P@ssw0rd2!")  # 一次迁移后的用户

        # ========== 第七阶段：历史密钥验证 ==========
        print("\n=== 阶段7：历史密钥验证 ===")

        print("尝试使用所有历史密钥解密:")
        historical_keys = [("初始密钥", key_before_rotate1), ("第一次迁移密钥", new_key1), ("当前密钥", new_key2)]

        for key_name, key in historical_keys:
            print(f"\n使用 {key_name} ({km.get_key_fingerprint(key)[:8]}):")
            test_crypto = CryptoManager(MigrationKeyManager(key))

            for user in test_users:
                user_file = test_db_dir / user["username"] / "dialogues.json"
                with open(user_file) as f:
                    encrypted = json.load(f)["password"]

                try:
                    decrypted = test_crypto.decrypt_password(encrypted)
                    status = "✅" if decrypted == user["password"] else "❌"
                    print(f"  {status} {user['username']}: {decrypted}")
                except Exception as e:
                    print(f"  ❌ {user['username']} 解密失败: {type(e).__name__}")

    print("\n【测试完成】临时目录已自动清理")
