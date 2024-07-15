import pgzrun
import time
import random
TITLE = "ETO"
TILE_SIZE = 20
WIDTH = 700
HEIGHT = 700
direction = 'up'
isLoose = False
score = 0
frame = 0
the = Actor(r"E:\杂物\我的项目\images\莹.jpg", [350, 350])
snkaeHead = Actor(r"E:\杂物\我的项目\images\黑.png")
snkaeHead.x = 360
snkaeHead.y = 360
cookie1 = Actor(r"E:\杂物\我的项目\images\picwish(1).png")
cookie2 = Actor(r"E:\杂物\我的项目\images\picwish(4).png")
cookie3 = Actor(r"E:\杂物\我的项目\images\picwish(7).png")
cookie4 = Actor(r"E:\杂物\我的项目\images\picwish(9).png")
cookie5 = Actor(r"E:\杂物\我的项目\images\picwish(12).png")
cookies = [cookie1, cookie2, cookie3, cookie4, cookie5]
cookie = cookies[frame]
x_0 = random.randint(5, 30)*TILE_SIZE
y_0 = random.randint(5, 30)*TILE_SIZE
x_1 = random.randint(5, 30)*TILE_SIZE
y_1 = random.randint(5, 30)*TILE_SIZE
Snake = []
Snake.append(snkaeHead)
for i in range(4):
    snakebody = Actor(r"E:\杂物\我的项目\images\黑.png")
    snakebody.x = Snake[i].x - TILE_SIZE
    snakebody.y = Snake[i].y
    Snake.append(snakebody)
def draw():
    screen.clear()
    the.draw()
    cookie = cookies[frame]
    cookie.x = x_0
    cookie.y = y_0
    cookie.draw()
    cookie.x = x_1
    cookie.y = y_1
    cookie.draw()
    roll = list(reversed(Snake))
    for snkaebody in roll:
        snkaebody.draw()
    screen.draw.text("Score:"+str(score), (300, 50), fontsize=50, color="pink")
    if isLoose:
        screen.draw.text("looser", (250, 270), fontsize=100, color="pink")
def update():
    global direction
    if keyboard.left or keyboard.A:
        direction = 'left'
    if keyboard.right or keyboard.D:
        direction = 'right'
    if keyboard.up or keyboard.W:
        direction = 'up'
    if keyboard.down or keyboard.S:
        direction = 'down'
def moveSnake():
    global direction, isLoose, score, frame, x_0, y_0, x_1, y_1
    newSnakeHead = Actor(r"E:\杂物\我的项目\images\黑.png")
    if frame < 4:
        frame += 1
    else:
        frame = 0
    if direction == 'right':
        newSnakeHead.x = Snake[0].x + TILE_SIZE
        newSnakeHead.y = Snake[0].y
    if direction == 'left':
        newSnakeHead.x = Snake[0].x - TILE_SIZE
        newSnakeHead.y = Snake[0].y
    if direction == 'up':
        newSnakeHead.x = Snake[0].x
        newSnakeHead.y = Snake[0].y - TILE_SIZE
    if direction == 'down':
        newSnakeHead.x = Snake[0].x
        newSnakeHead.y = Snake[0].y + TILE_SIZE
    if newSnakeHead.y < 0 or newSnakeHead.y > HEIGHT or newSnakeHead.x < 0 or newSnakeHead.x > WIDTH:
        isLoose = True
    for snakebody in Snake:
        if newSnakeHead.x == snakebody.x and newSnakeHead.y == snakebody.y:
            isLoose = True
            break
    if newSnakeHead.x == x_0 and newSnakeHead.y == y_0:
        x_0 = random.randint(5, 30)*TILE_SIZE
        y_0 = random.randint(5, 30)*TILE_SIZE
        score += 1
    elif newSnakeHead.x == x_1 and newSnakeHead.y == y_1:
        x_1 = random.randint(5, 30)*TILE_SIZE
        y_1 = random.randint(5, 30)*TILE_SIZE
        score += 1
    else:
        del Snake[len(Snake)-1]
    if isLoose == False:
        clock.schedule_unique(moveSnake, 0.1)
    Snake.insert(0, newSnakeHead)
moveSnake()
pgzrun.go()
