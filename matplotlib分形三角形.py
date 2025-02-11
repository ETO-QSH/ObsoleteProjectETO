import numpy as np
import matplotlib.pyplot as plt

class Triangle:
    def __init__(self, radius: float, center: tuple[float, float], angle: int, color: str, edge: str):
        """
        初始化三角形对象
        :param radius: 外接圆半径
        :param center: 三角形中心坐标 (x, y)
        :param angle: 朝向 -- 30 * self % 120
        :param color: 三角形填充颜色
        :param edge: 三角形边框颜色
        """
        self.radius = radius
        self.center = center
        self.angle = angle
        self.color = color
        self.edge = edge

    def get_vertices(self):
        angle = np.radians(30 * self.angle % 120)
        base_angles = np.radians([0, 120, 240])
        angles = (base_angles + angle) % (2 * np.pi)
        vertices = np.array([[self.center[0] + self.radius * np.cos(angle), self.center[1] + self.radius * np.sin(angle)] for angle in angles])
        return vertices

    def draw(self, ax):
        vertices = self.get_vertices()
        ax.fill(vertices[:, 0], vertices[:, 1], color=self.color, edgecolor=self.edge)



def fractalTriangle(iteration: int, radius: float, center: tuple[float, float], angle: int, color: str, edge: str, inter: str):
    triangles = [Triangle(radius*2, center, angle+2, inter, inter)]
    temp = [radius, center]
    iterCenter = [center]
    while iteration:
        centers = []
        while iterCenter:
            center = iterCenter.pop()
            triangles.append(Triangle(radius, center, angle, color, color))
            if angle % 4 == 0:
                center = [(center[0]+radius/2, center[1]-radius*(3**0.5/2)), (center[0]-radius, center[1]), (center[0]+radius/2, center[1]+radius*(3**0.5/2))]
            elif angle % 4 == 1:
                center = [(center[0], center[1]+radius), (center[0]+radius*(3**0.5/2), center[1]-radius/2), (center[0]-radius*(3**0.5/2), center[1]-radius/2)]
            elif angle % 4 == 2:
                center = [(center[0]-radius/2, center[1]-radius*(3**0.5/2)), (center[0]+radius, center[1]), (center[0]-radius/2, center[1]+radius*(3**0.5/2))]
            elif angle % 4 == 3:
                center = [(center[0], center[1]-radius), (center[0]+radius*(3**0.5/2), center[1]+radius/2), (center[0]-radius*(3**0.5/2), center[1]+radius/2)]
            centers += center
        iterCenter = centers[:]
        iteration -= 1
        radius /= 2
    triangles.append(Triangle(temp[0]*2, temp[1], angle+2, '#00000000', edge))
    return triangles


triangles = fractalTriangle(iteration=3, radius=2, center=(0, 0), angle=3, color='#FFbFbFFF', edge='#0000FF7F', inter='#7FFF7FFF')


# 创建绘图窗口
fig, ax = plt.subplots(figsize=(8, 8))

# 遍历列表绘制所有三角形
for triangle in triangles:
    triangle.draw(ax)

# 设置坐标轴范围和比例
ax.set_xlim(-5, 5)
ax.set_ylim(-5, 5)
ax.set_aspect('equal')  # 保持坐标轴比例相等

# 添加网格
ax.grid()

# 显示绘制结果
plt.show()