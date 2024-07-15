
from PIL import Image; import struct
file = '.\\images\\4k_new.png'; ima = Image.open(file); rgba = ima.convert('RGBA')   # 填写需要处理图片的相对路径
Str = ''.join([str(bin(rgba.getpixel((p, q))[o])[-1:]) for p in range(ima.width) for q in range(ima.height) for o in range(4)])
pic = open((file.rsplit('.', 1)[0]+'_new.'+''.join([chr(j) for j in [k for k in [int(Str[i:i+8], 2) for i in [32, 40, 48, 56]] if k != 0]])), 'wb')
[pic.write(struct.pack('B', int(''.join(k), 2))) for k in [[Str[64:64+8*int(Str[0:32], 2)][i*8+j] for j in range(8)] for i in range(int(Str[0:32], 2))]]
