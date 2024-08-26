import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import java.util.Random;

class Point {
    int X, Y;

    Point(int x, int y) {
        this.X = x;
        this.Y = y;
    }
}

class Chessman {
    String Name;
    int Value;
    Color Color;

    Chessman(String name, int value, Color color) {
        this.Name = name;
        this.Value = value;
        this.Color = color;
    }
}

class Checkerboard {
    private int _linePoints;
    private int[][] _checkerboard;

    Checkerboard(int linePoints) {
        this._linePoints = linePoints;
        this._checkerboard = new int[linePoints][linePoints];
    }

    public int[][] getCheckerboard() {
        return _checkerboard;
    }

    public boolean canDrop(Point point) {
        return _checkerboard[point.Y][point.X] == 0;
    }

    public Chessman drop(Chessman chessman, Point point) {
        System.out.println(chessman.Name + " (" + point.X + ", " + point.Y + ")");
        _checkerboard[point.Y][point.X] = chessman.Value;
        if (win(point)) {
            System.out.println(chessman.Name + "获胜");
            return chessman;
        }
        return null;
    }

    private boolean win(Point point) {
        int curValue = _checkerboard[point.Y][point.X];
        for (int[] os : Main.offset) {
            if (getCountOnDirection(point, curValue, os[0], os[1])) {
                return true;
            }
        }
        return false;
    }

    private boolean getCountOnDirection(Point point, int value, int xOffset, int yOffset) {
        int count = 1;
        for (int step = 1; step < 5; step++) {
            int x = point.X + step * xOffset;
            int y = point.Y + step * yOffset;
            if (0 <= x && x < _linePoints && 0 <= y && y < _linePoints && _checkerboard[y][x] == value) {
                count++;
            } else {
                break;
            }
        }
        for (int step = 1; step < 5; step++) {
            int x = point.X - step * xOffset;
            int y = point.Y - step * yOffset;
            if (0 <= x && x < _linePoints && 0 <= y && y < _linePoints && _checkerboard[y][x] == value) {
                count++;
            } else {
                break;
            }
        }
        return count >= 5;
    }
}

public class Main extends JFrame {
    private static final String TITLE = "ETO";
    public static final Chessman BLACK_CHESSMAN = new Chessman("黑子", 1, Color.BLACK);
    public static final Chessman WHITE_CHESSMAN = new Chessman("白子", 2, Color.WHITE);
    private static final int SIZE = 30;
    private static final int LINE_POINTS = 19;
    private static final int OUTER_WIDTH = 15;
    private static final int BORDER_WIDTH = 5;
    private static final int INSIDE_WIDTH = 5;
    private static final int BORDER_LENGTH = 555;
    private static final int START = 8;
    private static final int SCREEN_XY = 585;
    private static final int STONE_RADIUS = 10;
    public static final int[][] offset = {{1, 0}, {0, 1}, {1, 1}, {1, -1}};

    private Checkerboard checkerboard;
    private Chessman curRunner;
    private Chessman winner;
    private AI computer;
    private int blackWinCount = 0;
    private int whiteWinCount = 0;

    public Main() {
        setTitle(TITLE);
        setSize(SCREEN_XY, SCREEN_XY);
        setDefaultCloseOperation(EXIT_ON_CLOSE);
        setVisible(true);
        checkerboard = new Checkerboard(LINE_POINTS);
        curRunner = BLACK_CHESSMAN;
        computer = new AI(LINE_POINTS, WHITE_CHESSMAN);
        addMouseListener(new MouseAdapter() {
            public void mousePressed(MouseEvent e) {
                if (winner == null) {
                    java.awt.Point clickPos = e.getPoint(); // 获取鼠标点击的坐标点
                    Point clickPoint = getClickPoint(clickPos); // 转换为自定义的 Point 对象
                    if (clickPoint != null) {
                        if (checkerboard.canDrop(clickPoint)) {
                            winner = checkerboard.drop(curRunner, clickPoint);
                            if (winner == null) {
                                curRunner = getNext(curRunner);
                                computer.getOpponentDrop(clickPoint);
                                Point AI_point = computer.AI_drop();
                                winner = checkerboard.drop(curRunner, AI_point);
                                if (winner != null) {
                                    whiteWinCount++;
                                }
                            } else {
                                blackWinCount++;
                            }
                        } else {
                            System.out.println("超出棋盘区域");
                        }
                    }
                }
                repaint();
            }
        });
    }

    private Point getClickPoint(java.awt.Point clickPos) {
        int posX = clickPos.x - START;
        int posY = clickPos.y - START;
        if (posX < -INSIDE_WIDTH || posY < -INSIDE_WIDTH) {
            return null;
        }
        int x = posX / SIZE;
        int y = posY / SIZE;
        if (posX % SIZE > STONE_RADIUS) {
            x++;
        }
        if (posY % SIZE > STONE_RADIUS) {
            y++;
        }
        if (x >= LINE_POINTS || y >= LINE_POINTS) {
            return null;
        }
        return new Point(x, y);
    }

    private Chessman getNext(Chessman curRunner) {
        return curRunner == BLACK_CHESSMAN ? WHITE_CHESSMAN : BLACK_CHESSMAN;
    }

    @Override
    public void paint(Graphics g) {
        super.paint(g);
        drawCheckerboard(g);
        curRunner = getNext(curRunner);
        for (int i = 0; i < checkerboard.getCheckerboard().length; i++) {
            for (int j = 0; j < checkerboard.getCheckerboard()[i].length; j++) {
                if (checkerboard.getCheckerboard()[i][j] == BLACK_CHESSMAN.Value) {
                    drawChessman(g, new Point(j, i), BLACK_CHESSMAN.Color);
                } else if (checkerboard.getCheckerboard()[i][j] == WHITE_CHESSMAN.Value) {
                    drawChessman(g, new Point(j, i), WHITE_CHESSMAN.Color);
                }
            }
        }
        if (winner != null) {
            g.setColor(new Color(102, 204, 255));
            g.drawString(winner.Name + "获胜", (SCREEN_XY - 256) / 2, (SCREEN_XY - 64) / 2);
        }
    }

    private void drawCheckerboard(Graphics g) {
        // 绘制棋盘背景
        g.setColor(new Color(227, 146, 101));
        g.fillRect(OUTER_WIDTH, OUTER_WIDTH, SCREEN_XY - 2 * OUTER_WIDTH, SCREEN_XY - 2 * OUTER_WIDTH);

        // 绘制棋盘外边框
        g.setColor(Color.BLACK);
        g.drawRect(OUTER_WIDTH, OUTER_WIDTH, SCREEN_XY - 2 * OUTER_WIDTH, SCREEN_XY - 2 * OUTER_WIDTH);

        // 绘制棋盘内部的线条
        int startX = OUTER_WIDTH + START;
        int startY = OUTER_WIDTH + START;
        for (int i = 0; i < LINE_POINTS; i++) {
            g.drawLine(startX, startY + SIZE * i, startX + SIZE * (LINE_POINTS - 1), startY + SIZE * i);
            g.drawLine(startX + SIZE * i, startY, startX + SIZE * i, startY + SIZE * (LINE_POINTS - 1));
        }

        // 绘制特定位置的圆形标记
        for (int i : new int[]{3, 9, 15}) {
            for (int j : new int[]{3, 9, 15}) {
                int radius = (i == j && i == 9) ? 5 : 3;
                g.setColor(Color.BLACK); // 设置圆形标记的颜色
                g.fillOval(startX + SIZE * i - radius, startY + SIZE * j - radius, radius * 2, radius * 2);
            }
        }
    }

    private void drawChessman(Graphics g, Point point, Color stoneColor) {
        g.setColor(stoneColor);
        // 计算棋子中心位置
        int x = START + SIZE * point.X - SIZE / 2 - STONE_RADIUS;
        int y = START + SIZE * point.Y - SIZE / 2 - STONE_RADIUS;
        // 画出棋子
        g.fillOval(x, y, STONE_RADIUS * 2, STONE_RADIUS * 2);
    }

    public static void main(String[] args) {
        new Main();
    }
}

class AI {
    private int _linePoints;
    private Chessman _my;
    private Chessman _opponent;
    private int[][] _checkerboard;

    AI(int linePoints, Chessman chessman) {
        this._linePoints = linePoints;
        this._my = chessman;
        this._opponent = chessman == Main.WHITE_CHESSMAN ? Main.BLACK_CHESSMAN : Main.WHITE_CHESSMAN;
        this._checkerboard = new int[linePoints][linePoints];
    }

    public void getOpponentDrop(Point point) {
        _checkerboard[point.Y][point.X] = _opponent.Value;
    }

    public Point AI_drop() {
        Point point = null;
        int score = 0;
        for (int i = 0; i < _linePoints; i++) {
            for (int j = 0; j < _linePoints; j++) {
                if (_checkerboard[j][i] == 0) {
                    int _score = getPointScore(new Point(i, j));
                    if (_score > score) {
                        score = _score;
                        point = new Point(i, j);
                    } else if (_score == score && _score > 0) {
                        if (new Random().nextInt(100) % 2 == 0) {
                            point = new Point(i, j);
                        }
                    }
                }
            }
        }
        _checkerboard[point.Y][point.X] = _my.Value;
        return point;
    }

    private int getPointScore(Point point) {
        int score = 0;
        for (int[] os : Main.offset) {
            score += getDirectionScore(point, os[0], os[1]);
        }
        return score;
    }

    private int getDirectionScore(Point point, int xOffset, int yOffset) {
        int count = 0;
        int _count = 0;
        Boolean space = null;
        Boolean _space = null;
        int both = 0;
        int _both = 0;
        int flag = getStoneColor(point, xOffset, yOffset, true);
        if (flag != 0) {
            for (int step = 1; step < 6; step++) {
                int x = point.X + step * xOffset;
                int y = point.Y + step * yOffset;
                if (0 <= x && x < _linePoints && 0 <= y && y < _linePoints) {
                    if (flag == 1) {
                        if (_checkerboard[y][x] == _my.Value) {
                            count++;
                            if (space == Boolean.FALSE) {
                                space = true;
                            }
                        } else if (_checkerboard[y][x] == _opponent.Value) {
                            _both++;
                            break;
                        } else {
                            if (space == null) {
                                space = false;
                            } else {
                                break;
                            }
                        }
                    } else if (flag == 2) {
                        if (_checkerboard[y][x] == _my.Value) {
                            _both++;
                            break;
                        } else if (_checkerboard[y][x] == _opponent.Value) {
                            _count++;
                            if (_space == Boolean.FALSE) {
                                _space = true;
                            }
                        } else {
                            if (_space == null) {
                                _space = false;
                            } else {
                                break;
                            }
                        }
                    }
                } else {
                    if (flag == 1) {
                        both++;
                    } else if (flag == 2) {
                        _both++;
                    }
                }
            }
        }
        if (space == Boolean.FALSE) {
            space = null;
        }
        if (_space == Boolean.FALSE) {
            _space = null;
        }
        int _flag = getStoneColor(point, -xOffset, -yOffset, true);
        if (_flag != 0) {
            for (int step = 1; step < 6; step++) {
                int x = point.X - step * xOffset;
                int y = point.Y - step * yOffset;
                if (0 <= x && x < _linePoints && 0 <= y && y < _linePoints) {
                    if (_flag == 1) {
                        if (_checkerboard[y][x] == _my.Value) {
                            count++;
                            if (space == Boolean.FALSE) {
                                space = true;
                            }
                        } else if (_checkerboard[y][x] == _opponent.Value) {
                            _both++;
                            break;
                        } else {
                            if (space == null) {
                                space = false;
                            } else {
                                break;
                            }
                        }
                    } else if (_flag == 2) {
                        if (_checkerboard[y][x] == _my.Value) {
                            _both++;
                            break;
                        } else if (_checkerboard[y][x] == _opponent.Value) {
                            _count++;
                            if (_space == Boolean.FALSE) {
                                _space = true;
                            }
                        } else {
                            if (_space == null) {
                                _space = false;
                            } else {
                                break;
                            }
                        }
                    }
                } else {
                    if (_flag == 1) {
                        both++;
                    } else if (_flag == 2) {
                        _both++;
                    }
                }
            }
        }
        int score = 0;
        if (count == 4) {
            if (both == 0) {
                score = 100000;
            } else if (both == 1) {
                score = -10000;
            } else {
                score = -10000;
            }
        } else if (_count == 4) {
            score = 90000;
        } else if (count == 3) {
            if (both == 0) {
                score = 900;
            } else if (both == 1) {
                score = -90000000;
            } else {
                score = -1000000;
            }
        } else if (_count == 3) {
            if (_both == 0) {
                score = 819;
            } else if (_both == 1) {
                score = -819;
            } else {
                score = -900;
            }
        } else if (count == 2) {
            if (both == 0) {
                score = 90;
            } else if (both == 1) {
                score = -10;
            } else {
                score = 0;
            }
        } else if (_count == 2) {
            if (_both == 0) {
                score = 81;
            } else if (_both == 1) {
                score = 0;
            } else {
                score = -9;
            }
        } else if (count == 1) {
            score = 10;
        } else if (_count == 1) {
            score = 9;
        } else {
            score = 0;
        }
        if (space != null || _space != null) {
            score /= 2;
        }
        return score;
    }

    private int getStoneColor(Point point, int xOffset, int yOffset, boolean next) {
        int x = point.X + xOffset;
        int y = point.Y + yOffset;
        if (0 <= x && x < _linePoints && 0 <= y && y < _linePoints) {
            if (_checkerboard[y][x] == _my.Value) {
                return 1;
            } else if (_checkerboard[y][x] == _opponent.Value) {
                return 2;
            } else {
                if (next) {
                    return getStoneColor(new Point(x, y), xOffset, yOffset, false);
                } else {
                    return 0;
                }
            }
        } else {
            return 0;
        }
    }
}

