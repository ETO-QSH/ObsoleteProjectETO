import random
from manim import *

class Triangle(VGroup):
    def __init__(self, radius: float, center: tuple[float, float], angle: int, color: str, edge: str, opacity: float, z_index: int):
        """
        初始化三角形对象
        :param radius: 外接圆半径
        :param center: 三角形中心坐标 (x, y)
        :param angle: 朝向 -- 30 * self % 120
        :param color: 三角形填充颜色
        :param edge: 三角形边框颜色
        :param opacity: 三角形填充透明度
        :param z_index: 图形显示层级
        """
        super().__init__()
        angles = (np.radians([0, 120, 240]) + np.radians(30 * angle % 120)) % (2 * np.pi)
        vertices = [[center[0] + radius * np.cos(a), center[1] + radius * np.sin(a), 0] for a in angles]
        triangle = Polygon(*vertices, color=color, fill_color=color, fill_opacity=opacity, stroke_color=edge if edge else color, stroke_width=3 if edge else 0, z_index=z_index)
        self.add(triangle)


class FractalTriangleScene(Scene):
    def construct(self):
        self.add(Triangle(radius=4, center=(0, 0), angle=1, color='#7FFF7F', edge='#7F7FFF', opacity=1.0, z_index=1))
        self.add(Triangle(radius=4, center=(0, 0), angle=1, color='#000000', edge='#000000', opacity=0.0, z_index=3))
        self.add(Triangle(radius=4, center=(0, 0), angle=3, color='#7FFF7F', edge='#7F7FFF', opacity=1.0, z_index=1))
        self.add(Triangle(radius=4, center=(0, 0), angle=3, color='#000000', edge='#000000', opacity=0.0, z_index=3))

        triangles = fractalTriangle(iteration=5, radius=2, center=(0, 0), angle=3, color='#FF0000', opacity=0.5)
        iteration, animations = 5, []
        for i in range(iteration):
            shuffled_list = triangles[(3**i-1)//2:(3**(i+1)-1)//2]
            random.shuffle(shuffled_list)
            for shape in shuffled_list:
                shape.shift(UP * 8)
                delay = random.uniform(0, 0.5) + i * 0.5
                anim = ApplyMethod(shape.shift, DOWN * 8).set_run_time(0.5)
                anim.on_start = lambda: shape.set_z_index(4)
                anim.on_finish = lambda: shape.set_z_index(2)
                animations.append(Succession(Wait(delay), anim))
        self.play(AnimationGroup(*animations))
        self.wait(0.5)

        triangles = fractalTriangle(iteration=5, radius=2, center=(0, 0), angle=1, color='#0000FF', opacity=0.5)
        iteration, animations = 5, []
        for i in range(iteration):
            shuffled_list = triangles[(3**i-1)//2:(3**(i+1)-1)//2]
            random.shuffle(shuffled_list)
            for shape in shuffled_list:
                shape.shift(UP * 8)
                delay = random.uniform(0, 0.5) + i * 0.5
                anim = ApplyMethod(shape.shift, DOWN * 8).set_run_time(0.5)
                anim.on_start = lambda: shape.set_z_index(4)
                anim.on_finish = lambda: shape.set_z_index(2)
                animations.append(Succession(Wait(delay), anim))
        self.play(AnimationGroup(*animations))
        self.wait(0.5)


def fractalTriangle(iteration: int, radius: float, center: tuple[float, float], angle: int, color: str, opacity: float):
    triangles = []
    iterCenter = [center]
    while iteration:
        centers = []
        while iterCenter:
            center = iterCenter.pop(0)
            triangles.append(Triangle(radius=radius, center=center, angle=angle, color=color, edge='', opacity=opacity, z_index=2))
            if angle % 4 == 0:
                centers.append((center[0] - radius, center[1]))
                centers.append((center[0] + radius / 2, center[1] - radius * (3 ** 0.5 / 2)))
                centers.append((center[0] + radius / 2, center[1] + radius * (3 ** 0.5 / 2)))
            elif angle % 4 == 1:
                centers.append((center[0], center[1] + radius))
                centers.append((center[0] + radius * (3 ** 0.5 / 2), center[1] - radius / 2))
                centers.append((center[0] - radius * (3 ** 0.5 / 2), center[1] - radius / 2))
            elif angle % 4 == 2:
                centers.append((center[0] + radius, center[1]))
                centers.append((center[0] - radius / 2, center[1] - radius * (3 ** 0.5 / 2)))
                centers.append((center[0] - radius / 2, center[1] + radius * (3 ** 0.5 / 2)))
            elif angle % 4 == 3:
                centers.append((center[0], center[1] - radius))
                centers.append((center[0] + radius * (3 ** 0.5 / 2), center[1] + radius / 2))
                centers.append((center[0] - radius * (3 ** 0.5 / 2), center[1] + radius / 2))
        iterCenter = centers[:]
        iteration -= 1
        radius /= 2
    return triangles
