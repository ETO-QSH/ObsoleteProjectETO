import pgzrun
import time
import random
TITLE = "ETO"
TILE_SIZE = 20
WIDTH = 700
HEIGHT = 700
direction_0 = 'up'
direction_1 = 'up'
isLoose = False
kill = 2
frame = 0
score_0 = 0
score_1 = 0
the = Actor(r"C:\PY\我的项目\images\莹.jpg", [350, 350])
snkaeHead_0 = Actor(r"C:\PY\我的项目\images\黑.png")
snkaeHead_1 = Actor(r"C:\PY\我的项目\images\白.png")
snkaeHead_0.x = 340
snkaeHead_0.y = 540
snkaeHead_1.x = 380
snkaeHead_1.y = 540
cookie_1 = Actor(r"C:\PY\我的项目\images\picwish(1).png")
cookie_2 = Actor(r"C:\PY\我的项目\images\picwish(4).png")
cookie_3 = Actor(r"C:\PY\我的项目\images\picwish(7).png")
cookie_4 = Actor(r"C:\PY\我的项目\images\picwish(9).png")
cookie_5 = Actor(r"C:\PY\我的项目\images\picwish(12).png")
cookies = [cookie_1, cookie_2, cookie_3, cookie_4, cookie_5]
cookie = cookies[frame]
x_0 = random.randint(1, 34)*TILE_SIZE
y_0 = random.randint(1, 34)*TILE_SIZE
x_1 = random.randint(1, 34)*TILE_SIZE
y_1 = random.randint(1, 34)*TILE_SIZE
Snake_0 = []
Snake_1 = []
Snake_0.append(snkaeHead_0)
Snake_1.append(snkaeHead_1)
for i in range(4):
    snakebody_0 = Actor(r"C:\PY\我的项目\images\黑.png")
    snakebody_0.x = Snake_0[i].x - TILE_SIZE
    snakebody_0.y = Snake_0[i].y
    Snake_0.append(snakebody_0)
    snakebody_1 = Actor(r"C:\PY\我的项目\images\白.png")
    snakebody_1.x = Snake_1[i].x + TILE_SIZE
    snakebody_1.y = Snake_1[i].y
    Snake_1.append(snakebody_1)
def draw():
    screen.clear()
    the.draw()
    cookie = cookies[frame]
    cookie.x = x_0
    cookie.y = y_0    
    cookie.draw()
    cookie = cookies[frame]
    cookie.x = x_1
    cookie.y = y_1
    cookie.draw()
    roll_0 = list(reversed(Snake_0))
    roll_1 = list(reversed(Snake_1))
    for snkaebody_0 in roll_0:
        snkaebody_0.draw()
    for snkaebody_1 in roll_1:
        snkaebody_1.draw()
    screen.draw.text("Score:"+str(score_0)+"-"+str(score_1), (275, 50), fontsize=50, color="pink")
    if isLoose==True:
        if kill==0:
            screen.draw.text("White Win", (185, 100), fontsize=100, color="pink")
        elif kill==1:
            screen.draw.text("Black Win", (185, 100), fontsize=100, color="pink")
        elif score_0 > score_1:
            screen.draw.text("Black Win", (185, 100), fontsize=100, color="pink")
        elif score_0 < score_1:
            screen.draw.text("White Win", (185, 100), fontsize=100, color="pink")
        elif score_0 == score_1:
            screen.draw.text("Nobody Win", (160, 100), fontsize=100, color="pink")
def update():
    global direction_0, direction_1
    if keyboard.A:
        direction_0 = 'left'
    if keyboard.D:
        direction_0 = 'right'
    if keyboard.W:
        direction_0 = 'up'
    if keyboard.S:
        direction_0 = 'down'
    if keyboard.left:
        direction_1 = 'left'
    if keyboard.right:
        direction_1 = 'right'
    if keyboard.up:
        direction_1 = 'up'
    if keyboard.down:
        direction_1 = 'down'
def moveSnake():
    global direction_0, direction_1, score_0, score_1, snakebody_0, snakebody_1, isLoose, frame, kill, x_0, y_0 ,x_1, y_1
    if frame < 4:
        frame += 1
    else:
        frame = 0
    newSnakeHead_0 = Actor(r"C:\PY\我的项目\images\黑.png")
    newSnakeHead_1 = Actor(r"C:\PY\我的项目\images\白.png")
    if direction_0 == 'right':
        newSnakeHead_0.x = Snake_0[0].x + TILE_SIZE
        newSnakeHead_0.y = Snake_0[0].y
    if direction_0 == 'left':
        newSnakeHead_0.x = Snake_0[0].x - TILE_SIZE
        newSnakeHead_0.y = Snake_0[0].y
    if direction_0 == 'up':
        newSnakeHead_0.x = Snake_0[0].x
        newSnakeHead_0.y = Snake_0[0].y - TILE_SIZE
    if direction_0 == 'down':
        newSnakeHead_0.x = Snake_0[0].x
        newSnakeHead_0.y = Snake_0[0].y + TILE_SIZE
    if direction_1 == 'right':
        newSnakeHead_1.x = Snake_1[0].x + TILE_SIZE
        newSnakeHead_1.y = Snake_1[0].y
    if direction_1 == 'left':
        newSnakeHead_1.x = Snake_1[0].x - TILE_SIZE
        newSnakeHead_1.y = Snake_1[0].y
    if direction_1 == 'up':
        newSnakeHead_1.x = Snake_1[0].x
        newSnakeHead_1.y = Snake_1[0].y - TILE_SIZE
    if direction_1 == 'down':
        newSnakeHead_1.x = Snake_1[0].x
        newSnakeHead_1.y = Snake_1[0].y + TILE_SIZE
    if newSnakeHead_0.x == x_0 and newSnakeHead_0.y == y_0:
        x_0 = random.randint(1, 34)*TILE_SIZE
        y_0 = random.randint(1, 34)*TILE_SIZE
        score_0 += 1
    elif newSnakeHead_0.x == x_1 and newSnakeHead_0.y == y_1:
        x_1 = random.randint(1, 34)*TILE_SIZE
        y_1 = random.randint(1, 34)*TILE_SIZE
        score_0 += 1
    else:
        del Snake_0[len(Snake_0)-1]
    if newSnakeHead_1.x == x_0 and newSnakeHead_1.y == y_0:
        x_0 = random.randint(1, 34)*TILE_SIZE
        y_0 = random.randint(1, 34)*TILE_SIZE
        score_1 += 1
    elif newSnakeHead_1.x == x_1 and newSnakeHead_1.y == y_1:
        x_1 = random.randint(1, 34)*TILE_SIZE
        y_1 = random.randint(1, 34)*TILE_SIZE
        score_1 += 1
    else:
        del Snake_1[len(Snake_1)-1]
    for snakebody_0 in Snake_0:
        if newSnakeHead_0.x == snakebody_0.x and newSnakeHead_0.y == snakebody_0.y:
            kill = 0
            isLoose = True
        elif newSnakeHead_1.x == snakebody_0.x and newSnakeHead_1.y == snakebody_0.y:
            kill = 1
            isLoose = True
            break
    for snakebody_1 in Snake_1:
        if newSnakeHead_1.x == snakebody_1.x and newSnakeHead_1.y == snakebody_1.y:
            kill = 1
            isLoose = True
        elif newSnakeHead_0.x == snakebody_1.x and newSnakeHead_0.y == snakebody_1.y:
            kill = 0
            isLoose = True
            break
    if newSnakeHead_0.y < 0 or newSnakeHead_0.y > HEIGHT or newSnakeHead_0.x < 0 or newSnakeHead_0.x > WIDTH:
        kill = 0
        isLoose = True
    if newSnakeHead_1.y < 0 or newSnakeHead_1.y > HEIGHT or newSnakeHead_1.x < 0 or newSnakeHead_1.x > WIDTH:
        kill = 1
        isLoose = True
    if newSnakeHead_1.x == newSnakeHead_0.x and newSnakeHead_1.y == newSnakeHead_0.y:
        kill = 2
        isLoose = True
    if isLoose == False:
        clock.schedule_unique(moveSnake, 0.1)
    Snake_0.insert(0, newSnakeHead_0)
    Snake_1.insert(0, newSnakeHead_1)
moveSnake()
pgzrun.go()
