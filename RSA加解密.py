
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding

# 生成密钥对
def generate_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key

# 保存密钥
def save_keys(private_key, public_key, private_key_path, public_key_path, password):
    encryption = serialization.BestAvailableEncryption(password)
    pem_private_key = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=encryption
    )
    pem_public_key = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open(private_key_path, "wb") as f:
        f.write(pem_private_key)
    with open(public_key_path, "wb") as f:
        f.write(pem_public_key)

# 加载密钥
def load_keys(private_key_path, public_key_path, password):
    with open(private_key_path, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=password,
            backend=default_backend()
        )
    with open(public_key_path, "rb") as f:
        public_key = serialization.load_pem_public_key(
            f.read(),
            backend=default_backend()
        )
    return private_key, public_key

# 加密文件（分块加密）
def encrypt_file(file_path, public_key):
    # 计算块大小
    key_size_bytes = public_key.key_size // 8
    hash_algorithm = hashes.SHA256()
    hash_size = hash_algorithm.digest_size
    chunk_size = key_size_bytes - 2 * hash_size - 2

    with open(file_path, "rb") as f:
        data = f.read()
    encrypted_data = []
    # 使用分块处理数据
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i+chunk_size]
        encrypted_chunk = public_key.encrypt(
            chunk,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hash_algorithm),
                algorithm=hash_algorithm,
                label=None
            )
        )
        encrypted_data.append(encrypted_chunk)
    # 将加密的块连接起来
    encrypted_data = b''.join(encrypted_data)

    # 保存加密文件
    filepath, filename = os.path.split(file_path)
    name, suffix = os.path.splitext(filename)
    encrypted_file_path = os.path.join(filepath, name + '.enc')

    with open(encrypted_file_path, "wb") as f:
        f.write(encrypted_data)
    print(f"文件已加密并保存到：{encrypted_file_path}")

# 解密文件（分块解密）
def decrypt_file(encrypted_file_path, private_key):
    # 计算块大小
    key_size_bytes = private_key.key_size // 8
    hash_algorithm = hashes.SHA256()
    hash_size = hash_algorithm.digest_size
    chunk_size = key_size_bytes - 2 * hash_size - 2

    with open(encrypted_file_path, "rb") as f:
        encrypted_data = f.read()
    
    decrypted_data = []
    # 使用分块处理密文
    for i in range(0, len(encrypted_data), key_size_bytes):
        encrypted_chunk = encrypted_data[i:i+key_size_bytes]
        decrypted_chunk = private_key.decrypt(
            encrypted_chunk,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hash_algorithm),
                algorithm=hash_algorithm,
                label=None
            )
        )
        decrypted_data.append(decrypted_chunk)
    # 将解密的块连接起来
    decrypted_data = b''.join(decrypted_data)

    # 保存解密文件
    decrypted_file_path = encrypted_file_path.replace(".enc", ".eto")
    with open(decrypted_file_path, "wb") as f:
        f.write(decrypted_data)
    print(f"文件已解密并保存到：{decrypted_file_path}")


if __name__ == "__main__":

    import os, argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description='RSA加解密')
    parser.add_argument('-f', required=True, help='需要加密的文件')
    parser.add_argument('-k', required=True, help='使用密钥的密码')
    parser.add_argument('-m', required=True, help='加密:True 解密:False')

    args = parser.parse_args()

    if Path(args.f).is_file():

        # 文件路径和密钥密码
        file_path, password = args.f, args.k
        key_password = password.encode('utf-8')
        private_key_path = "private_key.pem"
        public_key_path = "public_key.pem"

        if args.m == 'True':

            # 生成密钥对并保存
            private_key, public_key = generate_keys()
            save_keys(private_key, public_key, private_key_path, public_key_path, key_password)

            # 加密文件
            encrypt_file(file_path, public_key)

        elif args.m == 'False':
            
            # 加载密钥
            private_key, public_key = load_keys(private_key_path, public_key_path, key_password)

            # 解密文件
            filepath, filename = os.path.split(file_path)
            name, suffix = os.path.splitext(filename)
            encrypted_file_path = os.path.join(filepath, name + '.enc')
            decrypt_file(encrypted_file_path, private_key)

        else:
            parser.print_help()
    else:
        parser.print_help()
