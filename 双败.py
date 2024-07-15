import random

o = 0; p = 0; q = 0

for i in range(100000):
    List = []
    for i in range(4):
        # 10000:10100为最强者的胜率平均为1/2
        # 100:200为最强者的胜率平均为5/8
        # 100:10000为最强者的胜率平均为2/3
        List.append(random.randint(100, 10000))
    print(List)

    def game(x, y):
        test = []
        for i in range(x):
            test.append(0)
        for i in range(y):
            test.append(1)
        return random.choice(test)

    # 0号和1号中a为胜者
    if game(List[0], List[1]) == 0:
        a, c = List[0], List[1]
    else:
        a, c = List[1], List[0]

    # 2号和3号中b为胜者
    if game(List[2], List[3]) == 0:
        b, d = List[2], List[3]
    else:
        b, d = List[3], List[2]

    # 胜者组：e双胜，g进入败者组
    if game(a, b) == 0:
        e, g = a, b
    else:
        e, g = b, a

    # 败者组：h淘汰，f留在败者组
    if game(c, d) == 0:
        f, h = c, d
    else:
        f, h = d, c

    # 败者组：j淘汰，i进入胜者组
    if game(g, f) == 0:
        i, j = g, f
    else:
        i, j = f, g

    # 胜者组：e,i进行决赛
    z = game(e, i)

    # 淘汰赛制最强者胜率用o/p表示
    # 双败赛制最强者胜率用q/p表示
    if List[0] != List[1] != List[2] != List[3]:
        if e == max(List):
            o += 1
            if z == 0:
                q += 1
        elif i == max(List) and z == 1:
            q += 1
        p += 1

print(q/p, o/p)
