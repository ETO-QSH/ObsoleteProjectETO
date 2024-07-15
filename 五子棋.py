import os
import sys
import random
import pygame
from pygame.locals import *
import pygame.gfxdraw
from collections import namedtuple
TITLE = "ETO"
Chessman = namedtuple('Chessman', 'Name Value Color')
Point = namedtuple('Point', 'X Y')
BLACK_CHESSMAN = Chessman('黑子', 1, (0, 0, 0))
WHITE_CHESSMAN = Chessman('白子', 2, (255, 255, 255))
offset = [(1, 0), (0, 1), (1, 1), (1, -1)]
SIZE = 30  # 棋盘每个点时间的间隔
Line_Points = 19  # 棋盘每⾏/每列点数
Outer_Width = 15  # 棋盘外宽度
Border_Width = 5  # 边框宽度
Inside_Width = 5  # 边框跟实际的棋盘之间的间隔
Border_Length = 555  # 边框线的长度Border_Length = SIZE * (Line_Points - 1) + Inside_Width * 2 + Border_Width
Start = int(22.5)  # ⽹格线起点（左上角）坐标Outer_Width + int(Border_Width / 2) + Inside_Width
SCREEN_XY = 585  # 游戏屏幕的⾼SIZE * (Line_Points - 1) + Outer_Width * 2 + Border_Width + Inside_Width * 2
Stone_Radius = 10  # 棋⼦半径SIZE // 3


class Checkerboard:
    def __init__(self, line_points):
        self._line_points = line_points
        self._checkerboard = [[0] * line_points for _ in range(line_points)]

    def _get_checkerboard(self):
        return self._checkerboard
    checkerboard = property(_get_checkerboard)
    # 判断是否可落⼦

    def can_drop(self, point):
        return self._checkerboard[point.Y][point.X] == 0

    def drop(self, chessman, point):
        """
落⼦
        :param chessman:
        :param point:落⼦位置
        :return:若该⼦落下之后即可获胜，则返回获胜⽅，否则返回 None
        """
        # 把⿊棋/⽩棋落⼦的坐标打印出来
        print(f'{chessman.Name} ({point.X}, {point.Y})')
        self._checkerboard[point.Y][point.X] = chessman.Value
        # 打印获胜⽅出来
        if self._win(point):
            print(f'{chessman.Name}获胜')
            return chessman
    # 判断是否赢了

    def _win(self, point):
        cur_value = self._checkerboard[point.Y][point.X]
        for os in offset:
            if self._get_count_on_direction(point, cur_value, os[0], os[1]):

                return True
    # 判断是否赢了的代码，从这⾥往上看，代码都是正着写，反着看，写代码思路缺什么补什么，所以从这⾥开始看
    # 声明⼀个函数，按⽅向数数，数满5个就获胜。
    # ⼀个⼆维坐标上，判断上下、左右、两个45度直线，是否有五个相同的直连棋⼦，只要满⾜五颗⼦，则游戏结束:

    def _get_count_on_direction(self, point, value, x_offset, y_offset):
        count = 1
        for step in range(1, 5):
            x = point.X + step * x_offset
            y = point.Y + step * y_offset
            if 0 <= x < self._line_points and 0 <= y < self._line_points and self._checkerboard[y][x] == value:
                count += 1
            else:
                break
        for step in range(1, 5):
            x = point.X - step * x_offset
            y = point.Y - step * y_offset
            if 0 <= x < self._line_points and 0 <= y < self._line_points and self._checkerboard[y][x] == value:
                count += 1
            else:
                break
        return count >= 5


def print_text(screen, font, x, y, text, fcolor):
    screen.blit(font.render(text, True, fcolor), (x, y))


def getpath(path, kind):
    if hasattr(sys, "_MEIPASS"):
        if kind == "fonts":
            return os.path.join(sys._MEIPASS + path.replace("./fonts/", "\\fonts\\"))
        elif kind == "images":
            return os.path.join(sys._MEIPASS + path.replace("../images/", "\\images\\"))
    return os.path.join(path)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_XY, SCREEN_XY))
    pygame.display.set_caption('ETO')
    font = pygame.font.Font(getpath('./fonts/stxinwei.ttf', "fonts"), 64)
    checkerboard = Checkerboard(Line_Points)
    cur_runner = BLACK_CHESSMAN
    winner = None
    computer = AI(Line_Points, WHITE_CHESSMAN)
    # 设置⿊⽩双⽅初始连⼦为0
    black_win_count = 0
    white_win_count = 0
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_RETURN:
                    if winner is not None:
                        winner = None
                        cur_runner = BLACK_CHESSMAN
                        checkerboard = Checkerboard(Line_Points)
                        computer = AI(Line_Points, WHITE_CHESSMAN)
            elif event.type == MOUSEBUTTONDOWN:  # 检测⿏标落下
                if winner is None:  # 检测是否有⼀⽅胜出
                    pressed_array = pygame.mouse.get_pressed()
                    if pressed_array[0]:
                        mouse_pos = pygame.mouse.get_pos()
                        click_point = _get_clickpoint(mouse_pos)
                        if click_point is not None:  # 检测⿏标是否在棋盘内点击
                            if checkerboard.can_drop(click_point):
                                winner = checkerboard.drop(
                                    cur_runner, click_point)
                                if winner is None:  # 再次判断是否有胜出
                                    # ⼀个循环内检测两次，意思就是⼈出⼀次检测⼀下，电脑出⼀次检测⼀下。
                                    cur_runner = _get_next(cur_runner)
                                    computer.get_opponent_drop(click_point)
                                    AI_point = computer.AI_drop()
                                    winner = checkerboard.drop(
                                        cur_runner, AI_point)
                                    if winner is not None:
                                        white_win_count += 1
                                    cur_runner = _get_next(cur_runner)
                                else:
                                    black_win_count += 1
                        else:
                            print('超出棋盘区域')
        # 画棋盘
        _draw_checkerboard(screen)
        # 画棋盘上已有的棋⼦
        for i, row in enumerate(checkerboard.checkerboard):
            for j, cell in enumerate(row):
                if cell == BLACK_CHESSMAN.Value:
                    _draw_chessman(screen, Point(j, i), BLACK_CHESSMAN.Color)
                elif cell == WHITE_CHESSMAN.Value:
                    _draw_chessman(screen, Point(j, i), WHITE_CHESSMAN.Color)
        if winner:
            print_text(screen, font, ((SCREEN_XY) - 256) // 2,
                       ((SCREEN_XY) - 64) // 2, winner.Name + '获胜', (102, 204, 255))
        pygame.display.flip()


def _get_next(cur_runner):
    if cur_runner == BLACK_CHESSMAN:
        return WHITE_CHESSMAN
    else:
        return BLACK_CHESSMAN
# 画棋盘


def _draw_checkerboard(screen):
    # 填充棋盘背景⾊
    screen.fill((227, 146, 101))
    # 画棋盘⽹格线外的边框
    pygame.draw.rect(screen, (0, 0, 0), (Outer_Width,
                     Outer_Width, Border_Length, Border_Length), Border_Width)
    # 画⽹格线
    for i in range(Line_Points):
        pygame.draw.line(screen, (0, 0, 0), (Start, Start + SIZE * i),
                         (Start + SIZE * (Line_Points - 1), Start + SIZE * i), 1)
    for j in range(Line_Points):
        pygame.draw.line(screen, (0, 0, 0), (Start + SIZE * j, Start),
                         (Start + SIZE * j, Start + SIZE * (Line_Points - 1)), 1)
    # 画星位和天元
    for i in (3, 9, 15):
        for j in (3, 9, 15):
            if i == j == 9:
                radius = 5
            else:
                radius = 3
            # pygame.draw.circle(screen, BLACK, (Start + SIZE * i, Start + SIZE * j), radius)
            pygame.gfxdraw.aacircle(
                screen, Start + SIZE * i, Start + SIZE * j, radius, (0, 0, 0))
            pygame.gfxdraw.filled_circle(
                screen, Start + SIZE * i, Start + SIZE * j, radius, (0, 0, 0))

# 画棋⼦


def _draw_chessman(screen, point, stone_color):
    # pygame.draw.circle(screen, stone_color, (Start + SIZE * point.X, Start + SIZE * point.Y), Stone_Radius)
    pygame.gfxdraw.aacircle(screen, Start + SIZE * point.X,
                            Start + SIZE * point.Y, Stone_Radius, stone_color)
    pygame.gfxdraw.filled_circle(
        screen, Start + SIZE * point.X, Start + SIZE * point.Y, Stone_Radius, stone_color)

# 根据⿏标点击位置，返回游戏区坐标


def _get_clickpoint(click_pos):
    pos_x = click_pos[0] - Start
    pos_y = click_pos[1] - Start
    if pos_x < -Inside_Width or pos_y < -Inside_Width:
        return None
    x = pos_x // SIZE
    y = pos_y // SIZE
    if pos_x % SIZE > Stone_Radius:
        x += 1
    if pos_y % SIZE > Stone_Radius:
        y += 1
    if x >= Line_Points or y >= Line_Points:
        return None
    return Point(x, y)


class AI:
    def __init__(self, line_points, chessman):
        self._line_points = line_points
        self._my = chessman
        self._opponent = BLACK_CHESSMAN if chessman == WHITE_CHESSMAN else WHITE_CHESSMAN
        self._checkerboard = [[0] * line_points for _ in range(line_points)]

    def get_opponent_drop(self, point):
        self._checkerboard[point.Y][point.X] = self._opponent.Value

    def AI_drop(self):
        point = None
        score = 0
        for i in range(self._line_points):
            for j in range(self._line_points):
                if self._checkerboard[j][i] == 0:
                    _score = self._get_point_score(Point(i, j))
                    if _score > score:
                        score = _score
                        point = Point(i, j)
                    elif _score == score and _score > 0:
                        r = random.randint(0, 100)
                        if r % 2 == 0:
                            point = Point(i, j)
        self._checkerboard[point.Y][point.X] = self._my.Value
        return point

    def _get_point_score(self, point):
        score = 0
        for os in offset:
            score += self._get_direction_score(point, os[0], os[1])
        return score

    def _get_direction_score(self, point, x_offset, y_offset):
        count = 0  # 落⼦处我⽅连续⼦数
        _count = 0  # 落⼦处对⽅连续⼦数
        space = None  # 我⽅连续⼦中有⽆空格
        _space = None  # 对⽅连续⼦中有⽆空格
        both = 0  # 我⽅连续⼦两端有⽆阻挡
        _both = 0  # 对⽅连续⼦两端有⽆阻挡
        # 如果是 1 表⽰是边上是我⽅⼦，2 表⽰敌⽅⼦
        flag = self._get_stone_color(point, x_offset, y_offset, True)
        if flag != 0:
            for step in range(1, 6):
                x = point.X + step * x_offset
                y = point.Y + step * y_offset
                if 0 <= x < self._line_points and 0 <= y < self._line_points:
                    if flag == 1:
                        if self._checkerboard[y][x] == self._my.Value:
                            count += 1
                            if space is False:
                                space = True
                                space = True
                        elif self._checkerboard[y][x] == self._opponent.Value:
                            _both += 1
                            break
                        else:
                            if space is None:
                                space = False
                            else:
                                break  # 遇到第⼆个空格退出
                    elif flag == 2:
                        if self._checkerboard[y][x] == self._my.Value:
                            _both += 1
                            break
                        elif self._checkerboard[y][x] == self._opponent.Value:
                            _count += 1
                            if _space is False:
                                _space = True
                        else:
                            if _space is None:
                                _space = False
                            else:
                                break
                else:
                    # 遇到边也就是阻挡
                    if flag == 1:
                        both += 1
                    elif flag == 2:
                        _both += 1
        if space is False:
            space = None
        if _space is False:
            _space = None
        _flag = self._get_stone_color(point, -x_offset, -y_offset, True)
        if _flag != 0:
            for step in range(1, 6):
                x = point.X - step * x_offset
                y = point.Y - step * y_offset
                if 0 <= x < self._line_points and 0 <= y < self._line_points:
                    if _flag == 1:
                        if self._checkerboard[y][x] == self._my.Value:
                            count += 1
                            if space is False:
                                space = True
                        elif self._checkerboard[y][x] == self._opponent.Value:
                            _both += 1
                            break
                        else:
                            if space is None:
                                space = False
                            else:
                                break  # 遇到第⼆个空格退出
                    elif _flag == 2:
                        if self._checkerboard[y][x] == self._my.Value:
                            _both += 1
                            break
                        elif self._checkerboard[y][x] == self._opponent.Value:
                            _count += 1
                            if _space is False:
                                _space = True
                        else:
                            if _space is None:
                                _space = False
                            else:
                                break
                                break
                else:
                    # 遇到边也就是阻挡
                    if _flag == 1:
                        both += 1
                    elif _flag == 2:
                        _both += 1
        # 下⾯这⼀串score（分数）的含义：评估棋格获胜分数。
        # 使计算机计算获胜分值越⾼的棋格，就能确定能让⾃⼰的棋⼦最有可能达成联机的位置，也就是最佳进攻位置，
        # ⽽⼀旦计算机能确定⾃⼰的最⾼分值的位置，计算机就具备了进攻能⼒。
        # 同理，计算机能计算出玩家的最⼤分值位置，并抢先玩家获得该位置，这样计算机就具有了防御的能⼒。
        # 在计算机下棋之前，会计算空⽩棋格上的获胜分数，根据分数⾼低获取最佳位置。
        # 计算机会将棋⼦下在获胜分数最⾼的地⽅。
        # 当已放置4颗棋⼦时，必须在第五个空棋格上设置绝对⾼的分值。也就是10000
        # 当获胜组合上有部分位置已被对⼿的棋格占据⽽⽆法连成五⼦时，获胜组合上空棋格的获胜分数会直接设置为0。（四颗棋⼦，你把中间断了）
        # 当有两组及其以上的获胜组合位置交叉时，对该位置的分数进⾏叠加，形成分数⽐周围位置明显⾼。（五⼦棋中三三相连）
        score = 0
        if count == 4:
            if both == 0:
                score = 100000
            elif both == 1:
                score = -10000
            else:
                score = -10000
        elif _count == 4:
            score = 90000
        elif count == 3:
            if both == 0:
                score = 900
            elif both == 1:
                score = -90000000
            else:
                score = -1000000
        elif _count == 3:
            if _both == 0:
                score = 819
            elif _both == 1:
                score = -819
            else:
                score = -900
        elif count == 2:
            if both == 0:
                score = 90
            elif both == 1:
                score = -10
            else:
                score = 0
        elif _count == 2:
            if _both == 0:
                score = 81
            elif _both == 1:
                score = 0
            else:
                score = -9
        elif count == 1:
            score = 10
        elif _count == 1:
            score = 9
        else:
            score = 0
        if space or _space:
            score /= 2
        return score
    # 判断指定位置处在指定⽅向上是我⽅⼦、对⽅⼦、空

    def _get_stone_color(self, point, x_offset, y_offset, next):

        x = point.X + x_offset
        y = point.Y + y_offset
        if 0 <= x < self._line_points and 0 <= y < self._line_points:
            if self._checkerboard[y][x] == self._my.Value:
                return 1
            elif self._checkerboard[y][x] == self._opponent.Value:
                return 2
            else:
                if next:
                    return self._get_stone_color(Point(x, y), x_offset, y_offset, False)
                else:
                    return 0
        else:
            return 0


if __name__ == '__main__':
    main()
