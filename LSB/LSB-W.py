
from PIL import Image
pic, doc = '.\\images\\4k.png', '.\\images\\莹.jpg'  # 填写需要处理图片的相对路径, 填写需要处理文件的相对路径
ima, text = Image.open(pic), open(doc, 'rb').read(); old, new = ima.convert('RGBA'), Image.new('RGBA', ima.size)
text = list(''.join([(bin(len(text))[2:].zfill(32)+(''.join([bin(ord(i))[2:].zfill(8) for i in (doc.rsplit('.', 1)[1])]).zfill(32)))]+[(bin(i)[2:].zfill(8)) for i in text]))
[new.putpixel((p, q), tuple([int(i, 2) for i in [(''.join([bin(list(old.getpixel((p, q)))[o])[2:].zfill(8)]))[:7]+text[((p*ima.height+q)*4+o)]
 if ((p*ima.height+q)*4+o)<len(text) else (''.join([bin(list(old.getpixel((p, q)))[o])[2:].zfill(8)])) for o in range(4)]])) for p in range(ima.width) for q in range(ima.height)]
new.save(pic.rsplit('.', 1)[0] + '_new.png')
