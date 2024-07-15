import os; import sys; import math; import pgzrun; import random
cold = 0; item = []; keeps = []; WIDTH = 640; bullets = []; rects_0 = []; rects_1 = []; interval = 0; HEIGHT = 640; Rects = set(); TITLE = "ETO"
Rects_it = set(); Rects_red = set(); direction = "stop"; redtankdied = False; Rects_redwall = set(); redradian = random.randint(1, 360)
redtank_x = random.choice([50, 140, 230, 320, 410, 500, 590]); redtank_y = random.choice([50, 140, 230, 320, 410, 500, 590])
def getpath(path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS + path.replace("../images/", "\\images\\"))
    return os.path.join(path)
bullet = Actor(getpath("../images/雪球.png")); redtank = Actor(getpath("../images/红.png"), [redtank_x, redtank_y])
items = {getpath("../images/火山.png"): "火山", getpath("../images/黄昏.png"): "黄昏",
         getpath("../images/剑雨滂沱.png"): "剑雨滂沱", getpath("../images/极致火力.png"): "极致火力",
         getpath("../images/你须偿还.png"): "你须偿还", getpath("../images/枯荣共息.png"): "枯荣共息",
         getpath("../images/闭膛连发.png"): "闭膛连发", getpath("../images/秽壤的血脉.png"): "秽壤的血脉"}
maps = [[ 9 , 1 , 9 , 1 , 9 , 1 , 9 , 1 , 9 , 1 , 9 , 1 , 9 , 1 , 9 ],
        [ 0 , 9 ,"A", 9 ,"A", 9 ,"A", 9 ,"A", 9 ,"A", 9 ,"A", 9 , 0 ],
        [ 9 ,"B", 9 ,"B", 9 ,"B", 9 ,"B", 9 ,"B", 9 ,"B", 9 ,"B", 9 ],
        [ 0 , 9 ,"A", 9 ,"A", 9 ,"A", 9 ,"A", 9 ,"A", 9 ,"A", 9 , 0 ],
        [ 9 ,"B", 9 ,"B", 9 ,"B", 9 ,"B", 9 ,"B", 9 ,"B", 9 ,"B", 9 ],
        [ 0 , 9 ,"A", 9 ,"A", 9 ,"A", 9 ,"A", 9 ,"A", 9 ,"A", 9 , 0 ],
        [ 9 ,"B", 9 ,"B", 9 ,"B", 9 ,"B", 9 ,"B", 9 ,"B", 9 ,"B", 9 ],
        [ 0 , 9 ,"A", 9 ,"A", 9 ,"A", 9 ,"A", 9 ,"A", 9 ,"A", 9 , 0 ],
        [ 9 ,"B", 9 ,"B", 9 ,"B", 9 ,"B", 9 ,"B", 9 ,"B", 9 ,"B", 9 ],
        [ 0 , 9 ,"A", 9 ,"A", 9 ,"A", 9 ,"A", 9 ,"A", 9 ,"A", 9 , 0 ],
        [ 9 ,"B", 9 ,"B", 9 ,"B", 9 ,"B", 9 ,"B", 9 ,"B", 9 ,"B", 9 ],
        [ 0 , 9 ,"A", 9 ,"A", 9 ,"A", 9 ,"A", 9 ,"A", 9 ,"A", 9 , 0 ],
        [ 9 ,"B", 9 ,"B", 9 ,"B", 9 ,"B", 9 ,"B", 9 ,"B", 9 ,"B", 9 ],
        [ 0 , 9 ,"A", 9 ,"A", 9 ,"A", 9 ,"A", 9 ,"A", 9 ,"A", 9 , 0 ],
        [ 9 , 1 , 9 , 1 , 9 , 1 , 9 , 1 , 9 , 1 , 9 , 1 , 9 , 1 , 9 ]]
for desx in range(len(maps)):
    for desy in range(len(maps[desx])):
        if (maps[desx][desy] == "A"):
            maps[desx][desy] = random.choice([2, 2, 9, 9, 9])
        elif (maps[desx][desy] == "B"):
            maps[desx][desy] = random.choice([3, 3, 9, 9, 9])
        if (maps[desx][desy] == 0):
            rects_0.append(((45*desy, 45*(desx-1)), (10, 100)))
        elif (maps[desx][desy] == 1):
            rects_0.append(((45*(desy-1), 45*desx), (100, 10)))
        elif (maps[desx][desy] == 2):
            rects_1.append(((45*desy, 45*(desx-1)), (10, 100)))
        elif (maps[desx][desy] == 3):
            rects_1.append(((45*(desy-1), 45*desx), (100, 10)))
redtank.angle = redtank.angle + redradian; rects = rects_0 + rects_1
for o in range(len(rects)):
    for p in range(0, rects[o][1][0] + 1):
        for q in range(0, rects[o][1][1] + 1):
            Rects.add(((rects[o][0][0] + p), (rects[o][0][1] + q)))
def hoi(x1, y1, x2, y2, modle):
    if (x1 != x2):
        for z in range(0, (x1 - x2 + 1)):
            modle.add(((x2 + z), int(y2 + (z * ((y1 - y2) / (x1 - x2))))))
        for z in range(0, (x2 - x1 + 1)):
            modle.add(((x1 + z), int(y1 + (z * ((y2 - y1) / (x2 - x1))))))
    if (y1 != y2):
        for z in range(0, (y1 - y2 + 1)):
            modle.add((int(x2 + (z * ((x1 - x2) / (y1 - y2)))), (y2 + z)))
        for z in range(0, (y2 - y1 + 1)):
            modle.add((int(x1 + (z * ((x2 - x1) / (y2 - y1)))), (y1 + z)))
def draw():
    screen.clear(); screen.fill((245, 242, 233))
    for rect in (rects_1):
        screen.draw.filled_rect(Rect(rect), (228, 221, 196))
    for rect in (rects_0):
        screen.draw.filled_rect(Rect(rect), (213, 200, 160))
    for it in item:
        it.draw()
    for bullet in bullets:
        bullet.draw()
    redtank.draw(); Rects_red.clear(); Rects_redwall.clear()
def update():
    global direction
    if keyboard.W:
        direction = "up"
    if keyboard.S:
        direction = "down"
    if keyboard.A and keyboard.W:
        direction = "left and up"
    if keyboard.A and keyboard.S:
        direction = "left and down"
    if keyboard.D and keyboard.W:
        direction = "right and up"
    if keyboard.D and keyboard.S:
        direction = "right and down"
def move():
    global redtankdied, direction, interval, bullet, keep, cold, it
    hoi02_red = int(redtank.y - ((20 - 12 * math.tan(math.radians(redtank.angle))) * math.sin(math.radians(redtank.angle)) + 12 / math.cos(math.radians(redtank.angle))))
    hoi03_red = int(redtank.x + ((12 - 20 * math.tan(math.radians(redtank.angle))) * math.sin(math.radians(redtank.angle)) + 20 / math.cos(math.radians(redtank.angle))))
    hoi2_red = int(redtank.y - ((12 - 12 * math.tan(math.radians(redtank.angle))) * math.sin(math.radians(redtank.angle)) + 12 / math.cos(math.radians(redtank.angle))))
    hoi3_red = int(redtank.x + ((12 - 12 * math.tan(math.radians(redtank.angle))) * math.sin(math.radians(redtank.angle)) + 12 / math.cos(math.radians(redtank.angle))))
    hoi6_red = int(redtank.y + ((20 - 12 * math.tan(math.radians(redtank.angle))) * math.sin(math.radians(redtank.angle)) + 12 / math.cos(math.radians(redtank.angle))))
    hoi7_red = int(redtank.x - ((12 - 20 * math.tan(math.radians(redtank.angle))) * math.sin(math.radians(redtank.angle)) + 20 / math.cos(math.radians(redtank.angle))))
    hoi01_red = int(redtank.x + ((20 - 12 * math.tan(math.radians(redtank.angle))) * math.cos(math.radians(redtank.angle))))
    hoi04_red = int(redtank.y + ((12 - 20 * math.tan(math.radians(redtank.angle))) * math.cos(math.radians(redtank.angle))))
    hoi1_red = int(redtank.x + ((12 - 12 * math.tan(math.radians(redtank.angle))) * math.cos(math.radians(redtank.angle))))
    hoi4_red = int(redtank.y + ((12 - 12 * math.tan(math.radians(redtank.angle))) * math.cos(math.radians(redtank.angle))))
    hoi5_red = int(redtank.x - ((20 - 12 * math.tan(math.radians(redtank.angle))) * math.cos(math.radians(redtank.angle))))
    hoi8_red = int(redtank.y - ((12 - 20 * math.tan(math.radians(redtank.angle))) * math.cos(math.radians(redtank.angle))))
    hoi(hoi01_red, hoi02_red, hoi03_red, hoi04_red, Rects_redwall); hoi(hoi03_red, hoi04_red, hoi5_red, hoi6_red, Rects_redwall)
    hoi(hoi5_red, hoi6_red, hoi7_red, hoi8_red, Rects_redwall); hoi(hoi7_red, hoi8_red, hoi01_red, hoi02_red, Rects_redwall)
    hoi(hoi1_red, hoi2_red, hoi3_red, hoi4_red, Rects_red); hoi(hoi3_red, hoi4_red, hoi5_red, hoi6_red, Rects_red)
    hoi(hoi5_red, hoi6_red, hoi7_red, hoi8_red, Rects_red); hoi(hoi7_red, hoi8_red, hoi1_red, hoi2_red, Rects_red)
    vx = 2.4 * math.cos(math.radians(redtank.angle)); vy = 2.4 * math.sin(math.radians(redtank.angle))
    if (len(Rects & Rects_redwall) > 0):
        g = 0; h = 0; r = 0; s = 0; u = 640; v = 640; m = redtank.x - 3 * math.cos(math.radians(redtank.angle)); n = redtank.y + 3 * math.sin(math.radians(redtank.angle))
        for (p, q) in (Rects & Rects_redwall):
            g += p; h += q
            if (p > r):
                r = p
            if (q > s):
                s = q
            if (p < u):
                u = p
            if (q < v):
                v = q
        j = int(g / len(Rects & Rects_redwall)); k = int(h / len(Rects & Rects_redwall))
        if direction == "up" or direction == "left and up" or direction == "right and up":
            if (33.69 <= (redtank.angle % 360) <= 146.31):
                if ((j >= m) and (33.69 <= (redtank.angle % 360) <= 90) and ((r - m) >= 12)):
                    vx = 0; vy = (2 / 3) * vy
                elif ((j <= m) and (90 <= (redtank.angle % 360) <= 146.31) and ((u - m) <= -12)):
                    vx = 0; vy = (2 / 3) * vy
                if ((-15 <= (j - m) <= 15) and (v <= (n - 20))):
                    vy = 0
                print("1")
            elif (146.31 <= (redtank.angle % 360) <= 213.69):
                if ((k <= n) and (146.31 <= (redtank.angle % 360) <=200) and ((v - n) <= -12)):
                    vy = 0; vx = (2 / 3) * vx
                elif ((k >= n) and (180 <= (redtank.angle % 360) <= 213.69) and ((s - n) >= 12)):
                    vy = 0; vx = (2 / 3) * vx
                if ((-22.5 <= (k - n) <= 22.5) and (u <= (m - 20))):
                    vx = 0
                print("2")
            elif (213.69 <= (redtank.angle % 360) <= 326.31):
                if ((j <= m) and (213.69 <= (redtank.angle % 360) <= 270) and ((u - m) <= -12)):
                    vx = 0; vy = (2 / 3) * vy
                elif ((j >= m) and (270 <= (redtank.angle % 360) <= 326.31) and ((r - m) >= 12)):
                    vx = 0; vy = (2 / 3) * vy
                if ((-15 <= (j - m) <= 15) and (s >= (n + 20))):
                    vy = 0
                print("3")
            else:
                if ((k <= n) and (0 <= (redtank.angle % 360) <= 33.69) and ((v - n) <= -12)):
                    vy = 0; vx = (2 / 3) * vx
                elif ((k >= n) and (326.31 <= (redtank.angle % 360) <= 360) and ((s - n) >= 12)):
                    vy = 0; vx = (2 / 3) * vx
                if ((-22.5 <= (j - m) <= 22.5) and (r >= (m + 20))):
                    vx = 0
                print("4")
        if direction == "down" or direction == "left and down" or direction == "right and down":
            if (33.69 <= (redtank.angle % 360) <= 146.31):
                if ((j <= m) and (33.69 <= (redtank.angle % 360) <= 90) and ((u - m) <= -12)):
                    vx = 0; vy = (2 / 3) * vy
                elif ((j >= m) and (90 <= (redtank.angle % 360) <= 146.31) and ((r - m) >= 12)):
                    vx = 0; vy = (2 / 3) * vy
                if ((-15 <= (j - m) <= 15) and (s >= (n + 12))):
                    vy = 0
                print("5")
            elif (146.31 <= (redtank.angle % 360) <= 213.69):
                if ((k >= n) and (146.31 <= (redtank.angle % 360) <= 180) and ((v - n) <= 12)):
                    vy = 0; vx = (2 / 3) * vx
                elif ((k <= n) and (180 <= (redtank.angle % 360) <= 213.69) and ((v - n) <= -12)):
                    vy = 0; vx = (2 / 3) * vx
                if ((-22.5 <= (j - m) <= 22.5) and (r >= (m + 12))):
                    vx = 0
                print("6")
            elif (213.69 <= (redtank.angle % 360) <= 326.31):
                if ((j >= m) and (213.69 <= (redtank.angle % 360) <= 270) and ((r - m) >= 12)):
                    vx = 0; vy = (2 / 3) * vy
                elif ((j <= m) and (270 <= (redtank.angle % 360) <= 326.31) and ((u - m) <= -12)):
                    vx = 0; vy = (2 / 3) * vy
                if ((-15 <= (j - m) <= 15) and (v <= (n - 12))):
                    vy = 0
                print("7")
            else:
                if ((k >= n) and (0 <= (redtank.angle % 360) <= 33.69) and ((s - n) >= 12)):
                    vy = 0; vx = (2 / 3) * vx
                elif ((k <= n) and (326.31 <= (redtank.angle % 360) <= 360) and ((s - n) <= -12)):
                    vy = 0; vx = (2 / 3) * vx
                if ((-22.5 <= (k - n) <= 22.5) and (u <= (m - 12))):
                    vx = 0
                print("8")
    if direction == "up":
        redtank.x = redtank.x + vx; redtank.y = redtank.y - vy
    if direction == "down":
        redtank.x = redtank.x - vx; redtank.y = redtank.y + vy
    if direction == "left and up":
        redtank.angle = redtank.angle + 1.8; redtank.x = redtank.x + (2 / 3) * vx; redtank.y = redtank.y - (2 / 3) * vy
    if direction == "left and down":
        redtank.angle = redtank.angle + 1.8; redtank.x = redtank.x - (2 / 3) * vx; redtank.y = redtank.y + (2 / 3) * vy
    if direction == "right and up":
        redtank.angle = redtank.angle - 1.8; redtank.x = redtank.x + (2 / 3) * vx; redtank.y = redtank.y - (2 / 3) * vy
    if direction == "right and down":
        redtank.angle = redtank.angle - 1.8; redtank.x = redtank.x - (2 / 3) * vx; redtank.y = redtank.y + (2 / 3) * vy
    if keyboard.E and interval >= 10:
        bullet = Actor(getpath("../images/雪球.png"), [redtank.x + 25 * math.cos(math.radians(redtank.angle)), redtank.y - 25 * math.sin(math.radians(redtank.angle))])
        bullet.vx = 3.2 * math.cos(math.radians(redtank.angle)); bullet.vy = 3.2 * math.sin(math.radians(redtank.angle))
        keep = 0; interval = 0; bullet.angle = redtank.angle; bullets.append(bullet); keeps.append(keep)
    if cold >= 1000:
        cold = 0; r = random.randint(1, 7); items_x = random.choice([50, 140, 230, 320, 410, 500, 590])
        items_y = random.choice([50, 140, 230, 320, 410, 500, 590]); it = Actor(list(items)[r], [items_x, items_y])
        for th in item:
            if ((th.x, th.y) == (it.x, it.y)):
                del item[item.index(th)]
        it.r = r; item.append(it)
    for bullet in bullets:
        if ((((int(bullet.x + 5), int(bullet.y + 4)) in Rects) and ((int(bullet.x + 5), int(bullet.y + 2)) in Rects)) or
            (((int(bullet.x + 5), int(bullet.y - 4)) in Rects) and ((int(bullet.x + 5), int(bullet.y - 2)) in Rects)) or
            (((int(bullet.x - 5), int(bullet.y + 4)) in Rects) and ((int(bullet.x - 5), int(bullet.y + 2)) in Rects)) or
            (((int(bullet.x - 5), int(bullet.y - 4)) in Rects) and ((int(bullet.x - 5), int(bullet.y - 2)) in Rects))):
            bullet.vx = -bullet.vx
        if ((((int(bullet.x + 4), int(bullet.y + 5)) in Rects) and ((int(bullet.x + 2), int(bullet.y + 5)) in Rects)) or
            (((int(bullet.x - 4), int(bullet.y + 5)) in Rects) and ((int(bullet.x - 2), int(bullet.y + 5)) in Rects)) or
            (((int(bullet.x + 4), int(bullet.y - 5)) in Rects) and ((int(bullet.x + 2), int(bullet.y - 5)) in Rects)) or
            (((int(bullet.x - 4), int(bullet.y - 5)) in Rects) and ((int(bullet.x - 2), int(bullet.y - 5)) in Rects))):
            bullet.vy = -bullet.vy
        if (((int(bullet.x + 5), int(bullet.y + 3)) in Rects_red) or ((int(bullet.x + 5), int(bullet.y - 3)) in Rects_red) or
            ((int(bullet.x - 5), int(bullet.y + 3)) in Rects_red) or ((int(bullet.x - 5), int(bullet.y - 3)) in Rects_red) or
            ((int(bullet.x + 3), int(bullet.y + 5)) in Rects_red) or ((int(bullet.x - 3), int(bullet.y + 5)) in Rects_red) or
            ((int(bullet.x + 3), int(bullet.y - 5)) in Rects_red) or ((int(bullet.x - 3), int(bullet.y - 5)) in Rects_red)):
            print("BOOM!")
    if redtankdied == False:
        i = 0; cold += 1; interval += 1
        for it in item:
            i += 1
            for p in range(int(it.x - 7), int(it.x + 8)):
                Rects_it.add((p, int(it.y - 7))); Rects_it.add((p, int(it.y + 8)))
            for q in range(int(it.y - 7), int(it.y + 8)):
                Rects_it.add((int(it.x - 7), q)); Rects_it.add((int(it.x + 8), q))
            if len(Rects_red & Rects_it) != 0:
                print(items.get(list(items)[it.r])); del item[i-1]
            Rects_it.clear()
        for x in keeps:
            keeps[keeps.index(x)] += 1
            if 1000 in keeps:
                del bullets[0]; del keeps[0]
        for bullet in bullets:
            bullet.x += bullet.vx; bullet.y -= bullet.vy
        clock.schedule_unique(move, 0.01)
    direction = "stop"
move(); music.play("bgm"); pgzrun.go()
