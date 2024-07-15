import turtle
import re


def draw_line(start_x, start_y, end_x, end_y):
    screen = turtle.Screen()
    pen = turtle.Turtle()
    pen.speed(0)
    pen.hideturtle()
    pen.up()
    pen.goto(start_x-300, start_y-300)
    pen.down()
    pen.goto(end_x-300, end_y-300)


def SVGtransformation(path, X, Y, A):
    pattern0 = r'd=" M [0-9A-Z .]+"'
    pattern1 = r' \d+\.*\d*'
    with open(path, 'r') as file:
        content = file.read()
    matches0 = re.findall(pattern0, content)
    for text0 in matches0:
        matches1 = re.findall(pattern1, text0)
        number_list = []
        List = []
        for match in matches1:
            number = float(match[1:])
            number_list.append(number)
        for x, y in enumerate(number_list):
            if x%2 == 0:
                List.append((y, number_list[x+1]))
        for i in range(len(List)-1):
            draw_line(List[i][0], List[i][1], List[i+1][0], List[i+1][1])

SVGtransformation('frame-00001.svg', 0, 0, 0)
#draw_line(0, 0, 100, 100)