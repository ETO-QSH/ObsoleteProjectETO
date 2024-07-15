
from PIL import Image
import os
import re
tip = 0
text = str(open('.\\images\\try.jpg', 'rb').read())
textneed = list(text)
for p in range(len(textneed)):
    try:
        new = re.search(r'b\'[^\\]', text).span()[1]
        need = list('\\x' + textneed[new - 1].encode().hex())
        del textneed[new - 1]
        for q in reversed(need):
            textneed.insert((new - 1), q)
        text = ''.join(textneed)
    except AttributeError:
        pass
    try:
        new = re.search(r'\\[^x]', text).span()[1]
        need = list('x' + textneed[new - 1].encode().hex())
        del textneed[new - 1]
        for q in reversed(need):
            textneed.insert((new - 1), q)
        text = ''.join(textneed)
    except AttributeError:
        pass
    try:
        new = re.search(r'\\x[0-9a-f][0-9a-f][^\\]', text).span()[1]
        need = list('\\x' + textneed[new - 1].encode().hex())
        del textneed[new - 1]
        for q in reversed(need):
            textneed.insert((new - 1), q)
        text = ''.join(textneed)
    except AttributeError:
        pass
text = list(text.split('\\x')[1:-1])
for i in range(len(text)):
    text[i] = (bin(int(text[i], 16))[2:].zfill(8))
text.insert(0, bin(os.path.getsize('.\\images\\try.jpg'))[2:].zfill(8))
txt = open('.\\images\\新建文本文档.txt', 'w+')
ima = Image.open('.\\images\\ETO.png')
new = Image.new('RGBA', ima.size)
hides = list(''.join(text))
rgb = ima.convert('RGBA')
for p in range(ima.width):
    for q in range(ima.height):
        r, g, b, a = rgb.getpixel((p, q))
        try:
            r = (''.join(['0b', bin(r)[2:].zfill(8)]))[:9] + hides[tip]; tip += 1
        except IndexError:
            r = (''.join(['0b', bin(r)[2:].zfill(8)]))
        try:
            g = (''.join(['0b', bin(g)[2:].zfill(8)]))[:9] + hides[tip]; tip += 1
        except IndexError:
            g = (''.join(['0b', bin(g)[2:].zfill(8)]))
        try:
            b = (''.join(['0b', bin(b)[2:].zfill(8)]))[:9] + hides[tip]; tip += 1
        except IndexError:
            b = (''.join(['0b', bin(b)[2:].zfill(8)]))
        try:
            a = (''.join(['0b', bin(a)[2:].zfill(8)]))[:9] + hides[tip]; tip += 1
        except IndexError:
            a = (''.join(['0b', bin(a)[2:].zfill(8)]))
        print(r, g, b, a, file = txt)
txt = open('.\\images\\新建文本文档.txt', 'r+')
for i in range(0, ima.width):
    for j in range(0, ima.height):
        line = (txt.readline()).strip('\n').split(' ')
        new.putpixel((i, j), (int(line[0], 2), int(line[1], 2), int(line[2], 2), int(line[3], 2)))
#txt.close(); os.remove('.\\images\\新建文本文档.txt')
new.save('.\\images\\ETOnew.png')
