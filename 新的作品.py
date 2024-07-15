
import random
d = 0
for i in range(100000):
    a = random.randint(10000, 10100)
    b = random.randint(10000, 10100)
    if a>b :
        c = b/a
        d += c
    elif b>a:
        c = a/b
        d += c
    else:
        d += 1
print(d)
