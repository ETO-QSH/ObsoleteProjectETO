import pgzrun
import time

WIDTH = 600
HEIGHT = 766
TITLE = "ETO"

A1 = Actor(r"C:\PY\我的项目\images\北.png", [56, 223])
A2 = Actor(r"C:\PY\我的项目\images\北.png", [219, 223])
A3 = Actor(r"C:\PY\我的项目\images\北.png", [381, 223])
A4 = Actor(r"C:\PY\我的项目\images\北.png", [544, 223])
A5 = Actor(r"C:\PY\我的项目\images\北.png", [56, 386])
A6 = Actor(r"C:\PY\我的项目\images\北.png", [219, 386])
A7 = Actor(r"C:\PY\我的项目\images\北.png", [381, 386])
A8 = Actor(r"C:\PY\我的项目\images\北.png", [544, 386])
A9 = Actor(r"C:\PY\我的项目\images\北.png", [56, 548])
A10 = Actor(r"C:\PY\我的项目\images\北.png", [219, 548])
A11 = Actor(r"C:\PY\我的项目\images\北.png", [381, 548])
A12 = Actor(r"C:\PY\我的项目\images\北.png", [544, 548])
A13 = Actor(r"C:\PY\我的项目\images\北.png", [56, 711])
A14 = Actor(r"C:\PY\我的项目\images\北.png", [219, 711])
A15 = Actor(r"C:\PY\我的项目\images\北.png", [381, 711])
A16 = Actor(r"C:\PY\我的项目\images\北.png", [544, 711])
the = Actor(r"C:\PY\我的项目\images\背景.jpg", [300, 383])

s = 0; k = 0; p = 0; a1 = 0; a2 = 0; a3 = 0; a4 = 0; a5 = 0; a6 = 0; a7 = 0
a8 = 0; a9 = 0; a10 = 0; a11 = 0; a12 = 0; a13 = 0; a14 = 0; a15 = 0; a16 = 0

def draw():
    the.draw(); A1.draw(); A2.draw(); A3.draw(); A4.draw(); A5.draw(); A6.draw(); A7.draw()
    A8.draw(); A9.draw(); A10.draw(); A11.draw(); A12.draw(); A13.draw(); A14.draw(); A15.draw(); A16.draw()
    screen.draw.text("Step:" + str(s), (236, 45),
                     fontsize=50, color="pink")
    screen.draw.text("Score:" + str(a1 + a2 + a3 + a4 + a5 + a6 + a7 + a8 + a9 + a10 +
                     a11 + a12 + a13 + a14 + a15 + a16), (236, 90), fontsize=50, color="pink")

def on_mouse_down(pos, button):
    global k; global p; global s; global a1; global a2; global a3; global a4; global a5; global a6; global a7
    global a8; global a9; global a10; global a11; global a12; global a13; global a14; global a15; global a16

    while True:
        if (A1.collidepoint(pos) and p == 0 and button == mouse.LEFT) or k == 1:
            a1 += 1; A1.angle = A1.angle - 90
            if (k != 1):
                s += 1
            else:
                k = 0
            if (a1 % 4 == 1):
                k = 2
            elif (a1 % 4 == 2):
                k = 5
            elif (a1 % 4 == 3):
                pass
            elif (a1 % 4 == 0):
                pass
        if (A2.collidepoint(pos) and p == 0 and button == mouse.LEFT) or k == 2:
            a2 += 1; A2.angle = A2.angle - 90
            if (k != 2):
                s += 1
            else:
                k = 0
            if (a2 % 4 == 1):
                k = 3
            elif (a2 % 4 == 2):
                k = 6
            elif (a2 % 4 == 3):
                k = 1
            elif (a2 % 4 == 0):
                pass
        if (A3.collidepoint(pos) and p == 0 and button == mouse.LEFT) or k == 3:
            a3 += 1; A3.angle = A3.angle - 90
            if (k != 3):
                s += 1
            else:
                k = 0
            if (a3 % 4 == 1):
                k = 4
            elif (a3 % 4 == 2):
                k = 7
            elif (a3 % 4 == 3):
                k = 2
            elif (a3 % 4 == 0):
                pass
        if (A4.collidepoint(pos) and p == 0 and button == mouse.LEFT) or k == 4:
            a4 += 1; A4.angle = A4.angle - 90
            if (k != 4):
                s += 1
            else:
                k = 0
            if (a4 % 4 == 1):
                pass
            elif (a4 % 4 == 2):
                k = 8
            elif (a4 % 4 == 3):
                k = 3
            elif (a4 % 4 == 0):
                pass
        if (A5.collidepoint(pos) and p == 0 and button == mouse.LEFT) or k == 5:
            a5 += 1; A5.angle = A5.angle - 90
            if (k != 5):
                s += 1
            else:
                k = 0
            if (a5 % 4 == 1):
                k = 6
            elif (a5 % 4 == 2):
                k = 9
            elif (a5 % 4 == 3):
                pass
            elif (a5 % 4 == 0):
                k = 1
        if (A6.collidepoint(pos) and p == 0 and button == mouse.LEFT) or k == 6:
            a6 += 1; A6.angle = A6.angle - 90
            if (k != 6):
                s += 1
            else:
                k = 0
            if (a6 % 4 == 1):
                k = 7
            elif (a6 % 4 == 2):
                k = 10
            elif (a6 % 4 == 3):
                k = 5
            elif (a6 % 4 == 0):
                k = 2
        if (A7.collidepoint(pos) and p == 0 and button == mouse.LEFT) or k == 7:
            a7 += 1; A7.angle = A7.angle - 90
            if (k != 7):
                s += 1
            else:
                k = 0
            if (a7 % 4 == 1):
                k = 8
            elif (a7 % 4 == 2):
                k = 11
            elif (a7 % 4 == 3):
                k = 6
            elif (a7 % 4 == 0):
                k = 3
        if (A8.collidepoint(pos) and p == 0 and button == mouse.LEFT) or k == 8:
            a8 += 1; A8.angle = A8.angle - 90
            if (k != 8):
                s += 1
            else:
                k = 0
            if (a8 % 4 == 1):
                pass
            elif (a8 % 4 == 2):
                k = 12
            elif (a8 % 4 == 3):
                k = 7
            elif (a8 % 4 == 0):
                k = 4
        if (A9.collidepoint(pos) and p == 0 and button == mouse.LEFT) or k == 9:
            a9 += 1; A9.angle = A9.angle - 90
            if (k != 9):
                s += 1
            else:
                k = 0
            if (a9 % 4 == 1):
                k = 10
            elif (a9 % 4 == 2):
                k = 13
            elif (a9 % 4 == 3):
                pass
            elif (a9 % 4 == 0):
                k = 5
        if (A10.collidepoint(pos) and p == 0 and button == mouse.LEFT) or k == 10:
            a10 += 1; A10.angle = A10.angle - 90
            if (k != 10):
                s += 1
            else:
                k = 0
            if (a10 % 4 == 1):
                k = 11
            elif (a10 % 4 == 2):
                k = 14
            elif (a10 % 4 == 3):
                k = 9
            elif (a10 % 4 == 0):
                k = 6
        if (A11.collidepoint(pos) and p == 0 and button == mouse.LEFT) or k == 11:
            a11 += 1; A11.angle = A11.angle - 90
            if (k != 11):
                s += 1
            else:
                k = 0
            if (a11 % 4 == 1):
                k = 12
            elif (a11 % 4 == 2):
                k = 15
            elif (a11 % 4 == 3):
                k = 10
            elif (a11 % 4 == 0):
                k = 7
        if (A12.collidepoint(pos) and p == 0 and button == mouse.LEFT) or k == 12:
            a12 += 1; A12.angle = A12.angle - 90
            if (k != 12):
                s += 1
            else:
                k = 0
            if (a12 % 4 == 1):
                pass
            elif (a12 % 4 == 2):
                k = 16
            elif (a12 % 4 == 3):
                k = 11
            elif (a12 % 4 == 0):
                k = 8
        if (A13.collidepoint(pos) and p == 0 and button == mouse.LEFT) or k == 13:
            a13 += 1; A13.angle = A13.angle - 90
            if (k != 13):
                s += 1
            else:
                k = 0
            if (a13 % 4 == 1):
                k = 14
            elif (a13 % 4 == 2):
                pass
            elif (a13 % 4 == 3):
                pass
            elif (a13 % 4 == 0):
                k = 9
        if (A14.collidepoint(pos) and p == 0 and button == mouse.LEFT) or k == 14:
            a14 += 1; A14.angle = A14.angle - 90
            if (k != 14):
                s += 1
            else:
                k = 0
            if (a14 % 4 == 1):
                k = 15
            elif (a14 % 4 == 2):
                pass
            elif (a14 % 4 == 3):
                k = 13
            elif (a14 % 4 == 0):
                k = 10
        if (A15.collidepoint(pos) and p == 0 and button == mouse.LEFT) or k == 15:
            a15 += 1; A15.angle = A15.angle - 90
            if (k != 15):
                s += 1
            else:
                k = 0
            if (a15 % 4 == 1):
                k = 16
            elif (a15 % 4 == 2):
                pass
            elif (a15 % 4 == 3):
                k = 14
            elif (a15 % 4 == 0):
                k = 11
        if (A16.collidepoint(pos) and p == 0 and button == mouse.LEFT) or k == 16:
            a16 += 1; A16.angle = A16.angle - 90
            if (k != 16):
                s += 1
            else:
                k = 0
            if (a16 % 4 == 1):
                pass
            elif (a16 % 4 == 2):
                pass
            elif (a16 % 4 == 3):
                k = 15
            elif (a16 % 4 == 0):
                k = 12
        if (the.collidepoint(pos) and button == mouse.LEFT):
            p = 1
        if (k == 0):
            p = 0
            break

pgzrun.go()
