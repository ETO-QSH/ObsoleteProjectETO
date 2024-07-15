

import zlib
doc = '.\\images\\r.0.0.mca'
mca = open(doc, 'rb').read()

def a(x, z):
    tip = 4 * ((x % 32) + (z % 32) * 32)
    print(mca[tip: tip + 3])
    tips = 4096 * int(str(mca[tip: tip + 3])[2:-1].replace('\\x', ''), 16)
    print(mca[tips: tips + 4])
    tipss = int(str(mca[tips: tips + 4])[2:-1].replace('\\x', ''), 16)
    print(tipss)
    tipsss = mca[tips + 5: tips + 5 + tipss]
    print(tipsss)
    return tipsss


new_data = zlib.decompress(a(8, 0)).decode("utf-8", "ignore")
print(new_data)
