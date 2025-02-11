import bezier
import numpy as np
import matplotlib.pyplot as plt

# 给定的点：起点、中间点（曲线上）、终点
originPoint = np.array([
    [0, 0],
    [60, 620],
    [100, 880]
], dtype=np.float32)

# 设定中间点对应的参数t值
t = 0.5

# 分解点坐标
P0 = originPoint[0]
Pm = originPoint[1]
P2 = originPoint[2]

# 根据贝塞尔方程解中间控制点P1
# B(t) = (1-t)^2 P0 + 2t(1-t)P1 + t^2 P2 = Pm
P1 = (Pm - (1 - t)**2 * P0 - t**2 * P2) / (2 * t * (1 - t))

# 构造贝塞尔曲线节点（需转置为2x3）
nodes = np.array([P0, P1, P2]).T.astype(np.float64)  # 确保类型正确

# 创建二次贝塞尔曲线
curve = bezier.Curve(nodes, degree=2)

# 评估曲线上的点用于绘图
ts = np.linspace(0, 1, 1000)
points = curve.evaluate_multi(ts).T  # 转换为(100, 2)

# 提供一个x值，找到最接近给定x值的点
# given_x = 80
# closest_point = points[np.argmin(np.abs(np.int32(points[:, 0]) - given_x))]

# 提供一个y值，找到最接近给定y值的点
given_y = 755
closest_point = points[np.argmin(np.abs(np.int32(points[:, 1]) - given_y))]

plt.rcParams['font.sans-serif'] = ['Lolita']
plt.rcParams['axes.unicode_minus'] = False

# 绘制曲线和点
plt.figure(figsize=(10, 6))
plt.plot(points[:, 0], points[:, 1], c='pink', label='贝塞尔曲线', zorder=1)
plt.scatter(originPoint[:, 0], originPoint[:, 1], c='red', label='给定过点')
plt.scatter(P1[0], P1[1], c='green', label='计算控制点')

# 标记给定x值处的点
plt.scatter(closest_point[0], closest_point[1], c='blue', marker='x', label='给定x值处的点')
plt.text(int(closest_point[0])+2, int(closest_point[1]), f'({int(closest_point[0])}, {int(closest_point[1])})', fontsize=9, verticalalignment='center')

plt.xticks(np.arange(min(points[:, 0]), max(points[:, 0]) + 10, 10))
plt.yticks(np.arange(min(points[:, 1]), max(points[:, 1]) + 50, 50))

plt.title('严格经过三点的二次贝塞尔曲线', pad=20)
plt.grid(True)
plt.legend()
plt.show()
