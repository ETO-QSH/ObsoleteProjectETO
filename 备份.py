import os; import sys; import math; import pgzrun; import random
cold = 0; item = []; keeps = []; WIDTH = 640; bullets = []; rects_0 = []; rects_1 = []; interval = 0; HEIGHT = 640; Rects = set(); TITLE = "ETO"
Rects_it = set(); Rects_red = set(); direction = "stop"; redtankdied = False; Rects_redwall = set(); Rects_s_redwall = set(); redradian = random.randint(1, 360)
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
def go(modle_x, modle_y, modle_angle):
    Rects_s_redwall.clear()
    if direction == "up":
        modle_x = modle_x + vx; modle_y = modle_y - vy
    elif direction == "down":
        modle_x = modle_x - vx; modle_y = modle_y + vy
    elif direction == "left and up":
        modle_angle = modle_angle + red_angle; modle_x = modle_x + (2 / 3) * vx; modle_y = modle_y - (2 / 3) * vy
    elif direction == "right and up":
        modle_angle = modle_angle - red_angle; modle_x = modle_x + (2 / 3) * vx; modle_y = modle_y - (2 / 3) * vy
    elif direction == "left and down":
        modle_angle = modle_angle + red_angle; modle_x = modle_x - (2 / 3) * vx; modle_y = modle_y + (2 / 3) * vy
    elif direction == "right and down":
        modle_angle = modle_angle - red_angle; modle_x = modle_x - (2 / 3) * vx; modle_y = modle_y + (2 / 3) * vy
    hoi5_red = int(modle_x - ((20 - 12 * math.tan(math.radians(modle_angle))) * math.cos(math.radians(modle_angle))))
    hoi6_red = int(modle_y + ((20 - 12 * math.tan(math.radians(modle_angle))) * math.sin(math.radians(modle_angle)) + 12 / math.cos(math.radians(modle_angle))))
    hoi7_red = int(modle_x - ((12 - 20 * math.tan(math.radians(modle_angle))) * math.sin(math.radians(modle_angle)) + 20 / math.cos(math.radians(modle_angle))))
    hoi8_red = int(modle_y - ((12 - 20 * math.tan(math.radians(modle_angle))) * math.cos(math.radians(modle_angle))))
    hoi01_red = int(modle_x + ((20 - 12 * math.tan(math.radians(modle_angle))) * math.cos(math.radians(modle_angle))))
    hoi02_red = int(modle_y - ((20 - 12 * math.tan(math.radians(modle_angle))) * math.sin(math.radians(modle_angle)) + 12 / math.cos(math.radians(modle_angle))))
    hoi03_red = int(modle_x + ((12 - 20 * math.tan(math.radians(modle_angle))) * math.sin(math.radians(modle_angle)) + 20 / math.cos(math.radians(modle_angle))))
    hoi04_red = int(modle_y + ((12 - 20 * math.tan(math.radians(modle_angle))) * math.cos(math.radians(modle_angle))))
    hoi(hoi01_red, hoi02_red, hoi03_red, hoi04_red, Rects_s_redwall); hoi(hoi03_red, hoi04_red, hoi5_red, hoi6_red, Rects_s_redwall)
    hoi(hoi5_red, hoi6_red, hoi7_red, hoi8_red, Rects_s_redwall); hoi(hoi7_red, hoi8_red, hoi01_red, hoi02_red, Rects_s_redwall)
    print("len", len(Rects & (Rects_s_redwall))); print("z", z)
def cheak():
    global vx, vy, red_angle, z
    red_s_x = redtank.x; red_s_y = redtank.y; red_s_angle = redtank.angle; red_angle = 1.8; z = len(Rects & (Rects_redwall))
    go(red_s_x, red_s_y, red_s_angle); vx = 2.4 * math.cos(math.radians(red_s_angle)); vy = 2.4 * math.sin(math.radians(red_s_angle))
    if (len(Rects & (Rects_redwall)) > 0):
        vx = 0; go(red_s_x, red_s_y, red_s_angle)
        if (len(Rects & (Rects_redwall)) < z):
            return (vx, vy, red_angle)
        elif (len(Rects & (Rects_redwall)) > 0):
            vy = 0; go(red_s_x, red_s_y, red_s_angle)
            if (len(Rects & (Rects_redwall)) < z):
                return (vx, vy, red_angle)
            elif (len(Rects & (Rects_redwall)) > 0):
                red_angle = 0; go(red_s_x, red_s_y, red_s_angle)
                if (len(Rects & (Rects_redwall)) < z):
                    return (vx, vy, red_angle)
                elif (len(Rects & (Rects_redwall)) > 0):
                    vx = 0; vy = 0; go(red_s_x, red_s_y, red_s_angle)
                    if (len(Rects & (Rects_redwall)) < z):
                        return (vx, vy, red_angle)
                    elif (len(Rects & (Rects_redwall)) > 0):
                        vx = 0; red_angle = 0; go(red_s_x, red_s_y, red_s_angle)
                        if (len(Rects & (Rects_redwall)) < z):
                            return (vx, vy, red_angle)
                        elif (len(Rects & (Rects_redwall)) > 0):
                            vy = 0; red_angle = 0; go(red_s_x, red_s_y, red_s_angle)
                            if (len(Rects & (Rects_redwall)) < z):
                                return (vx, vy, red_angle)
                            elif (len(Rects & (Rects_redwall)) > 0):
                                vx = 0; vy = 0; red_angle = 0; go(red_s_x, red_s_y, red_s_angle)
                                return (vx, vy, red_angle)
def move():
    global redtankdied, direction, interval, bullet, keep, cold, it
    hoi1_red = int(redtank.x + ((12 - 12 * math.tan(math.radians(redtank.angle))) * math.cos(math.radians(redtank.angle))))
    hoi2_red = int(redtank.y - ((12 - 12 * math.tan(math.radians(redtank.angle))) * math.sin(math.radians(redtank.angle)) + 12 / math.cos(math.radians(redtank.angle))))
    hoi3_red = int(redtank.x + ((12 - 12 * math.tan(math.radians(redtank.angle))) * math.sin(math.radians(redtank.angle)) + 12 / math.cos(math.radians(redtank.angle))))
    hoi4_red = int(redtank.y + ((12 - 12 * math.tan(math.radians(redtank.angle))) * math.cos(math.radians(redtank.angle))))
    hoi01_red = int(redtank.x + ((20 - 12 * math.tan(math.radians(redtank.angle))) * math.cos(math.radians(redtank.angle))))
    hoi02_red = int(redtank.y - ((20 - 12 * math.tan(math.radians(redtank.angle))) * math.sin(math.radians(redtank.angle)) + 12 / math.cos(math.radians(redtank.angle))))
    hoi03_red = int(redtank.x + ((12 - 20 * math.tan(math.radians(redtank.angle))) * math.sin(math.radians(redtank.angle)) + 20 / math.cos(math.radians(redtank.angle))))
    hoi04_red = int(redtank.y + ((12 - 20 * math.tan(math.radians(redtank.angle))) * math.cos(math.radians(redtank.angle))))
    hoi5_red = int(redtank.x - ((20 - 12 * math.tan(math.radians(redtank.angle))) * math.cos(math.radians(redtank.angle))))
    hoi6_red = int(redtank.y + ((20 - 12 * math.tan(math.radians(redtank.angle))) * math.sin(math.radians(redtank.angle)) + 12 / math.cos(math.radians(redtank.angle))))
    hoi7_red = int(redtank.x - ((12 - 20 * math.tan(math.radians(redtank.angle))) * math.sin(math.radians(redtank.angle)) + 20 / math.cos(math.radians(redtank.angle))))
    hoi8_red = int(redtank.y - ((12 - 20 * math.tan(math.radians(redtank.angle))) * math.cos(math.radians(redtank.angle))))
    hoi(hoi01_red, hoi02_red, hoi03_red, hoi04_red, Rects_redwall); hoi(hoi03_red, hoi04_red, hoi5_red, hoi6_red, Rects_redwall)
    hoi(hoi5_red, hoi6_red, hoi7_red, hoi8_red, Rects_redwall); hoi(hoi7_red, hoi8_red, hoi01_red, hoi02_red, Rects_redwall)
    hoi(hoi1_red, hoi2_red, hoi3_red, hoi4_red, Rects_red); hoi(hoi3_red, hoi4_red, hoi5_red, hoi6_red, Rects_red)
    hoi(hoi5_red, hoi6_red, hoi7_red, hoi8_red, Rects_red); hoi(hoi7_red, hoi8_red, hoi1_red, hoi2_red, Rects_red)
    z = len(Rects & (Rects_redwall)); cheak(); print(vx, vy, red_angle)
    if direction == "up":
        redtank.x = redtank.x + vx; redtank.y = redtank.y - vy
    elif direction == "down":
        redtank.x = redtank.x - vx; redtank.y = redtank.y + vy
    elif direction == "left and up":
        redtank.angle = redtank.angle + red_angle; redtank.x = redtank.x + (2 / 3) * vx; redtank.y = redtank.y - (2 / 3) * vy
    elif direction == "right and up":
        redtank.angle = redtank.angle - red_angle; redtank.x = redtank.x + (2 / 3) * vx; redtank.y = redtank.y - (2 / 3) * vy
    elif direction == "left and down":
        redtank.angle = redtank.angle + red_angle; redtank.x = redtank.x - (2 / 3) * vx; redtank.y = redtank.y + (2 / 3) * vy
    elif direction == "right and down":
        redtank.angle = redtank.angle - red_angle; redtank.x = redtank.x - (2 / 3) * vx; redtank.y = redtank.y + (2 / 3) * vy
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
