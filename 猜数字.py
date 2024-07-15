import random
i = random.randint(1, 100)
for __count in range(100):
    x = int(input('你猜的数字？'))
    print(('你猜的数字为：' + str(x)))
    if (i > x):
        print('你猜小了')
        a = x
        b = i
    elif (i < x):
        print('你猜大了')
        a = i
        b = x
    else:
        print('winner')
        break
    if (b - a <= 10):
        if ((b - a) % 2 == 0):
            k = (a + 1)
            print(('它猜的数字为：' + str(k)))
        else:
            k = (a + 2)
            print(('它猜的数字为：' + str(k)))
            if (b - a == 1):
                k = (a + 1)
                print(('它猜的数字为：' + str(k)))
            elif (b - a == 0):
                k = a
                print(('它猜的数字为：' + str(k)))
    else:
        k = random.randint(a, b)
        print(('它猜的数字为：' + str(k)))
        if (k > x):
            print('它猜小了')
        elif (k < x):
            print('它猜大了')
        else:
            print('looser')
            break