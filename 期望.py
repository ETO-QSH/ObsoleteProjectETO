
import random

a = 5
N = 10

def test(a, N):
    for n in range(N):
        if random.randint(0, 100) < a * (n + 1):
            return n + 1
    return 0

List = [test(a, N) for i in range(1000)]

print(List)

flag_0 = 0
for i in List:
    if i != 0:
        flag_0 += 1
print('flag_0 =', flag_0/N)


flag_1 = 0
for i in List:
    if i != 0:
        flag_1 += i
print('flag_1 =', flag_1/(flag_0))


flag_2 = 0
for i in List:
    if i != 0:
        flag_2 += (i-flag_1)**2
print('flag_2 =', flag_2/flag_1)
