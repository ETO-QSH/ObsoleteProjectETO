import random

r = 0; s = 0; p = 0; Q = 0; l = 0; math = 0
play_1 = []; play_2 = []; play_3 = []; play_4 = []
score_1 = 0; score_2 = 0; score_3 = 0; score_4 = 0
focus_A = [[6, 6]]; focus_B = []
cardlists = [play_1, play_2, play_3, play_4]

maps = [[9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
        [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
        [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
        [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
        [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
        [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
        [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
        [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
        [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
        [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
        [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
        [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
        [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9]]

card = [[0, 0], [0, 1], [0, 2], [0, 3], [0, 4],
        [0, 5], [0, 6], [1, 1], [1, 2], [1, 3],
        [1, 4], [1, 5], [1, 6], [2, 2], [2, 3],
        [2, 4], [2, 5], [2, 6], [3, 3], [3, 4],
        [3, 5], [3, 6], [4, 4], [4, 5], [4, 6],
        [5, 5], [5, 6], [6, 6]]

while (((len(play_1) + len(play_2)) + len(play_3)) + len(play_4) < 28):
    if (len(play_1) < 7):
        x = random.randint(0, 27)
        if (card[x] not in play_1):
            play_1.append(card[x])
    elif (len(play_2) < 7):
        x = random.randint(0, 27)
        if ((card[x] not in play_1) and (card[x] not in play_2)):
            play_2.append(card[x])
    elif (len(play_3) < 7):
        x = random.randint(0, 27)
        if ((card[x] not in play_1) and (card[x] not in play_2) and (card[x] not in play_3)):
            play_3.append(card[x])
    elif (len(play_4) < 7):
        x = random.randint(0, 27)
        if ((card[x] not in play_1) and (card[x] not in play_2) and (card[x] not in play_3) and (card[x] not in play_4)):
            play_4.append(card[x])

for i in range(4):
    card_x = cardlists[i]
    for i in range(len(card_x) - 1, 0, -1):
        for k in range(i):
            if (card_x[k][0] > card_x[(k + 1)][0] or (card_x[k][0] == card_x[k+1][0] and card_x[k][1] > card_x[k+1][1])):
                i = card_x[k][0]; card_x[k][0] = card_x[(k + 1)][0]; card_x[(k + 1)][0] = i
                i = card_x[k][1]; card_x[k][1] = card_x[(k + 1)][1]; card_x[(k + 1)][1] = i

def printlist():
    global l, math, score_1, score_2, score_3, score_4
    print("\033[1;33m当前地图：\033[0m")
    for x in range(len(maps)):
        for y in range(len(maps[x])):
            if (x > 1 and x < (len(maps[x]) - 2) and y > 1 and y < (len(maps[x]) - 2) and
                maps[x][y] != 9 and maps[x - 1][y] != 9 and maps[x + 1][y] == 9 and 
                maps[x][y - 1] == 9 and maps[x][y + 1] == 9):
                if ([x + 2, y] not in focus_A):
                    focus_A.append([x + 2, y])
                if ([x, y - 2] not in focus_A):
                    focus_A.append([x, y - 2])
                if ([x, y + 2] not in focus_A):
                    focus_A.append([x, y + 2])
                if ([x + 1, y] not in focus_B):
                    focus_B.append([x + 1, y])
                math += maps[x][y]
            if (x > 1 and x < (len(maps[x]) - 2) and y > 1 and y < (len(maps[x]) - 2) and
                maps[x][y] != 9 and maps[x - 1][y] == 9 and maps[x + 1][y] != 9 and 
                maps[x][y - 1] == 9 and maps[x][y + 1] == 9):
                if ([x - 2, y] not in focus_A):
                    focus_A.append([x - 2, y])
                if ([x, y - 2] not in focus_A):
                    focus_A.append([x, y - 2])
                if ([x, y + 2] not in focus_A):
                    focus_A.append([x, y + 2])
                if ([x - 1, y] not in focus_B):
                    focus_B.append([x - 1, y])
                math += maps[x][y]
            if (x > 1 and x < (len(maps[x]) - 2) and y > 1 and y < (len(maps[x]) - 2) and
                maps[x][y] != 9 and maps[x - 1][y] == 9 and maps[x + 1][y] == 9 and 
                maps[x][y - 1] != 9 and maps[x][y + 1] == 9):
                if ([x - 2, y] not in focus_A):
                    focus_A.append([x - 2, y])
                if ([x + 2, y] not in focus_A):
                    focus_A.append([x + 2, y])
                if ([x, y + 2] not in focus_A):
                    focus_A.append([x, y + 2])
                if ([x, y + 1] not in focus_B):
                    focus_B.append([x, y + 1])
                math += maps[x][y]
            if (x > 1 and x < (len(maps[x]) - 2) and y > 1 and y < (len(maps[x]) - 2) and
                maps[x][y] != 9 and maps[x - 1][y] == 9 and maps[x + 1][y] == 9 and 
                maps[x][y - 1] == 9 and maps[x][y + 1] != 9):
                if ([x - 2, y] not in focus_A):
                    focus_A.append([x - 2, y])
                if ([x + 2, y] not in focus_A):
                    focus_A.append([x + 2, y])
                if ([x, y - 2] not in focus_A):
                    focus_A.append([x, y - 2])
                if ([x, y - 1] not in focus_B):
                    focus_B.append([x, y - 1])
                math += maps[x][y]
        print("\033[1;37m" + str(maps[x]) + "\033[0m", "\033[1;35m" + str(x) + "\033[0m")
    card_x = cardlists[p % 4]
    if ((math % 3) == 0 and l == 1):
        if (p == 0):
            score_1 += math
        if (p == 1):
            score_2 += math
        if (p == 2):
            score_3 += math
        if (p == 3):
            score_4 += math
    print("\033[1;35m 0  1  2  3  4  5  6  7  8  9  10 11 12\033[0m")
    print("\033[1;36m当前玩家：\033[0m", "\033[1;32m" + str((p % 4) + 1) + "\033[0m")
    print("\033[1;36m当前得分：\033[0m", "\033[1;32m" + str(score_1) + "\033[0m")
    print("\033[1;36m所有得分:\033[0m",
          "\033[1;32m play 1:\033[0m", "\033[1;32m" + str(score_1) + "\033[0m",
          "\033[1;32m play 2:\033[0m", "\033[1;32m" + str(score_2) + "\033[0m",
          "\033[1;32m play 3:\033[0m", "\033[1;32m" + str(score_3) + "\033[0m",
          "\033[1;32m play 4:\033[0m", "\033[1;32m" + str(score_4) + "\033[0m")
    print("\033[1;36m可用牌型：\033[0m", "\033[1;32m" + str(card_x) + "\033[0m")
    print("\033[1;36m可用焦点：\033[0m", "\033[1;32m" + str(focus_A + focus_B) + "\033[0m")

printlist()

while True:
    card_x = cardlists[p % 4]; p += 1
    a, b, c = map(str, input("\033[1;34m请输入：x坐标 y坐标 z次序  \033[0m").split())
    print("\033[1;30m----------------此处分割线----------------\033[0m")
    if (ord(a) == 69 and (ord(b)) == 84 and (ord(c)) == 79):
        math = 0; s += 1; l = 0
    else:
        l = 1; a = int(a); b = int(b); c = int(c)
    if (len(card_x) == 0):
        t_1 = 0; t_2 = 0; t_3 = 0; t_4 = 0
        for x in range(len(cardlists)):
            for y in range(len(cardlists[x])):
                 for z in range(len(cardlists[x][y])):
                    if (x == 0):
                        t_1 += cardlists[x][y][z]
                    elif (x == 1):
                        t_2 += cardlists[x][y][z]
                    elif (x == 2):
                        t_3 += cardlists[x][y][z]
                    elif (x == 3):
                        t_4 += cardlists[x][y][z]
        if ((p % 4) == 1):
            score_1 += (t_2 + t_3 + t_4)
        elif ((p % 4) == 2):
            score_2 += (t_1 + t_3 + t_4)
        elif ((p % 4) == 3):
            score_3 += (t_1 + t_2 + t_4)
        elif ((p % 4) == 0):
            score_4 += (t_1 + t_2 + t_3)
        print("\033[1;30m----------------此处分割线----------------\033[0m")
        print("\033[1;30m----------------此处分割线----------------\033[0m")
        print("\033[1;36m所有得分:\033[0m",
          "\033[1;32m play 1:\033[0m", "\033[1;32m" + str(score_1) + "\033[0m",
          "\033[1;32m play 2:\033[0m", "\033[1;32m" + str(score_2) + "\033[0m",
          "\033[1;32m play 3:\033[0m", "\033[1;32m" + str(score_3) + "\033[0m",
          "\033[1;32m play 4:\033[0m", "\033[1;32m" + str(score_4) + "\033[0m")
        break
    if (l == 0 and s == 4):
        t_1 = 0; t_2 = 0; t_3 = 0; t_4 = 0
        for x in range(len(cardlists)):
            for y in range(len(cardlists[x])):
                for z in range(len(cardlists[x][y])):
                    if (x == 0):
                        t_1 += cardlists[x][y][z]
                    elif (x == 1):
                        t_2 += cardlists[x][y][z]
                    elif (x == 2):
                        t_3 += cardlists[x][y][z]
                    elif (x == 3):
                        t_4 += cardlists[x][y][z]
        Max = [t_1, t_2, t_3, t_4]; win = []; w = 0
        for i in range(len(Max)):
            if (Max[i] == min(Max)):
                win.append(i)
        if (len(win) == 3):
            if (Max.index(max(Max)) == 0):
                score_2 += math.floor(max(Max) / 3)
                score_3 += math.floor(max(Max) / 3)
                score_4 += math.floor(max(Max) / 3)
            elif (Max.index(max(Max)) == 1):
                score_1 += math.floor(max(Max) / 3)
                score_3 += math.floor(max(Max) / 3)
                score_4 += math.floor(max(Max) / 3)
            elif (Max.index(max(Max)) == 2):
                score_1 += math.floor(max(Max) / 3)
                score_2 += math.floor(max(Max) / 3)
                score_4 += math.floor(max(Max) / 3)
            elif (Max.index(max(Max)) == 3):
                score_1 += math.floor(max(Max) / 3)
                score_2 += math.floor(max(Max) / 3)
                score_3 += math.floor(max(Max) / 3)
        elif (len(win) == 2):
            for i in range(len(win)):
                w += Max[i]
            if (0 not in win):
                score_1 += math.floor((168 - w) / 2)
            if (1 not in win):
                score_2 += math.floor((168 - w) / 2)
            if (2 not in win):
                score_3 += math.floor((168 - w) / 2)
            if (3 not in win):
                score_4 += math.floor((168 - w) / 2)
        elif (len(win) == 1):
            if (Max.index(min(Max)) == 0):
                score_1 += (t_2 + t_3 + t_4)
            elif (Max.index(min(Max)) == 1):
                score_2 += (t_1 + t_3 + t_4)
            elif (Max.index(min(Max)) == 2):
                score_3 += (t_1 + t_2 + t_4)
            elif (Max.index(min(Max)) == 3):
                score_4 += (t_1 + t_2 + t_3)
        print("\033[1;30m----------------此处分割线----------------\033[0m")
        print("\033[1;30m----------------此处分割线----------------\033[0m")
        print("\033[1;36m所有得分:\033[0m",
          "\033[1;32m play 1:\033[0m", "\033[1;32m" + str(score_1) + "\033[0m",
          "\033[1;32m play 2:\033[0m", "\033[1;32m" + str(score_2) + "\033[0m",
          "\033[1;32m play 3:\033[0m", "\033[1;32m" + str(score_3) + "\033[0m",
          "\033[1;32m play 4:\033[0m", "\033[1;32m" + str(score_4) + "\033[0m")
        break
    if ([a, b] in focus_A and 1 <= c <= len(card_x)):
        if (card_x[c - 1][0] == maps[a + 2][b] or card_x[c - 1][1] == maps[a + 2][b]):
            if (card_x[c - 1][0] == maps[a + 2][b]):
                maps[a + 1][b] = card_x[c - 1][0]; maps[a - 1][b] = card_x[c - 1][1]; Q = 1
            else:
                maps[a - 1][b] = card_x[c - 1][0]; maps[a + 1][b] = card_x[c - 1][1]; Q = 1
        elif (card_x[c - 1][0] == maps[a][b + 2] or card_x[c - 1][1] == maps[a][b + 2]):
            if (card_x[c - 1][0] == maps[a][b + 2]):
                maps[a][b + 1] = card_x[c - 1][0]; maps[a][b - 1] = card_x[c - 1][1]; Q = 1
            else:
                maps[a][b - 1] = card_x[c - 1][0]; maps[a][b + 1] = card_x[c - 1][1]; Q = 1
        elif (card_x[c - 1][0] == maps[a - 2][b] or card_x[c - 1][1] == maps[a - 2][b]):
            if (card_x[c - 1][0] == maps[a - 2][b]):
                maps[a - 1][b] = card_x[c - 1][0]; maps[a + 1][b] = card_x[c - 1][1]; Q = 1
            else:
                maps[a + 1][b] = card_x[c - 1][0]; maps[a - 1][b] = card_x[c - 1][1]; Q = 1
        elif (card_x[c - 1][0] == maps[a][b - 2] or card_x[c - 1][1] == maps[a][b - 2]):
            if (card_x[c - 1][0] == maps[a][b - 2]):
                maps[a][b - 1] = card_x[c - 1][0]; maps[a][b + 1] = card_x[c - 1][1]; Q = 1
            else:
                maps[a][b + 1] = card_x[c - 1][0]; maps[a][b - 1] = card_x[c - 1][1]; Q = 1
    if ([a, b] in focus_B and 1 <= c <= len(card_x)):
        if (card_x[c - 1][0] == card_x[c - 1][1] == (maps[a + 1][b] or maps[a - 1][b])):
            maps[a][b + 1] = card_x[c - 1][0]; maps[a][b - 1] = card_x[c - 1][1]; Q = 1
        elif (card_x[c - 1][0] == card_x[c - 1][1] == (maps[a][b + 1] or maps[a][b - 1])):
            maps[a + 1][b] = card_x[c - 1][0]; maps[a - 1][b] = card_x[c - 1][1]; Q = 1
    if ((Q == 1 or r == 0) and l == 1 and 1 <= c <= len(card_x)):
        if (r == 0):
            maps[a][b - 1] = card_x[c - 1][0]; maps[a][b + 1] = card_x[c - 1][1]
        maps[a][b] = 0; card_x = cardlists[(p % 4) - 1]; del card_x[c - 1]
        k = 0; s = 0; Q = 0; r += 1; math = 0
        if ([a, b] in focus_A):
            del focus_A[focus_A.index([a, b])]
        if ([a, b] in focus_B):
            del focus_B[focus_B.index([a, b])]
        printlist()
    elif (l == 0):
        printlist()
    else:
        p -= 1
        print("\033[1;31m你故意找茬是吧！\033[0m")
