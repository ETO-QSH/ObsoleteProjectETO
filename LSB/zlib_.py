
import zlib
data = ['asd','ard']

#data = 'abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz' \
#       'abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz'
print(len(data))
print(data)

# 压缩
compressed_data = zlib.compress(data.encode())  # 注意：这儿要以字节的形式传入
print(len(compressed_data))
print(compressed_data)
print(type(compressed_data))

# 解压
new_data = zlib.decompress(compressed_data).decode()
print(len(new_data))
print(new_data)
