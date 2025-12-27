""" 模块测试文件 """

"""
from database.datalib import get_ais, get_ships, get_excel

ais = get_ais()
print(ais.columns)

ships = get_ships()
print(ships.columns)

excel = get_excel()
print(f"{i}\n{j}" for i, j in excel.keys())
"""


"""
import os
from pathlib import Path
from anytree import Node, RenderTree


def build_tree_from_disk(root_path, parent_node, skip_keywords):
    for name in sorted(os.listdir(root_path)):
        full_path = os.path.join(root_path, name)
        if any(kw in name for kw in skip_keywords):
            continue

        if os.path.isdir(full_path):
            dir_node = Node(f"{name}/", parent=parent_node)
            build_tree_from_disk(full_path, dir_node, skip_keywords)
        else:
            Node(name, parent=parent_node)


root_node = Node("52HZ-byETO")

build_tree_from_disk(
    Path(__file__).parent, root_node,
    skip_keywords=[".git", ".idea", ".venv", "__pycache__"]
)

for pre, _, node in RenderTree(root_node):
    print(f"{pre}{node.name}")
"""


"""
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt

from pathlib import Path
from cartopy import crs, feature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter


CRS_MAP = crs.PlateCarree()
plt.rcParams['font.sans-serif'] = ['Lolita']

CORRIDOR_GEOJSON = Path('database/corridor/corridor.geojson')

DPI = 100
CELL_KM = 1
W, H = 640, 720
HEATMAP_SIZE = 480

corridor = gpd.read_file(CORRIDOR_GEOJSON).to_crs('EPSG:4326')
lon_min, lat_min, lon_max, lat_max = corridor.total_bounds

nx = int((lon_max - lon_min) * 111.32 / CELL_KM) + 1
ny = int((lat_max - lat_min) * 110.54 / CELL_KM) + 1
lons = np.linspace(lon_min, lon_max, nx + 1)
lats = np.linspace(lat_min, lat_max, ny + 1)

# ---------- 占位数据 ----------
rng = np.random.default_rng(42)
rho_demo = rng.integers(0, 60, (ny, nx))
C_demo = rng.integers(0, 30, (ny, nx))
speed_demo = rng.uniform(5, 25, (ny, nx))
teu_demo = rng.integers(0, 10000, (ny, nx))

# ---------- 四张图 ----------
files = ['rho', 'C', 'speed', 'teu']
titles = ['船舶密度', '航迹冲突', '平均航速', '运力分布']
demos = [rho_demo, C_demo, speed_demo, teu_demo]

for f, title, demo in zip(files, titles, demos):
    fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI)

    left, bottom = (W - HEATMAP_SIZE) / 2 / W, 0.1
    width, height = HEATMAP_SIZE / W, HEATMAP_SIZE / H

    ax = fig.add_axes((left, bottom, width, height), projection=CRS_MAP)
    ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=CRS_MAP)

    # 底图
    ax.add_feature(feature.LAND.with_scale('10m'), facecolor='lightgray')
    ax.add_feature(feature.COASTLINE.with_scale('10m'))
    ax.add_feature(feature.BORDERS.with_scale('10m'), linestyle=':')

    # 热力图
    im = ax.pcolormesh(lons, lats, demo, cmap='YlOrRd', transform=CRS_MAP)

    # 经纬度刻度 0.4°，精确到一位小数，四周都显示
    lon_start = np.round(lon_min, 1)
    lon_end = np.round(lon_max, 1)
    lat_start = np.round(lat_min, 1)
    lat_end = np.round(lat_max, 1)

    xticks = np.round(np.arange(lon_start + 0.2, lon_end, 0.4), 1)
    yticks = np.round(np.arange(lat_start + 0.2, lat_end, 0.4), 1)

    ax.set_xticks(xticks, crs=CRS_MAP)
    ax.set_yticks(yticks, crs=CRS_MAP)

    ax.xaxis.set_major_formatter(LongitudeFormatter(number_format='.1f'))
    ax.yaxis.set_major_formatter(LatitudeFormatter(number_format='.1f'))

    ax.tick_params(axis='both', labelsize=10, direction='out', length=5, width=1)
    ax.tick_params(axis='x', which='both', top=True, bottom=True, labeltop=True, labelbottom=True)
    ax.tick_params(axis='y', which='both', left=True, right=True, labelleft=True, labelright=True)

    fig.text(
        0.5, 0.9, ' '.join(t for t in f"上海港周边{title}热力图"),
        ha='center', va='center', fontsize=16, fontweight='bold'
    )

    fig.savefig(f'output/{f}_{W}x{H}.png', dpi=DPI)
    plt.close(fig)

    print(f"已生成：{title}图")
"""


"""
from HZ_QA.weight import plot_2h_risk

plot_2h_risk("HZ_QA/output/risk.csv", "HZ_QA/output/risk_plot.png")
"""


"""
import csv
import pathlib
from bs4 import BeautifulSoup


INPUT, OUTPUT = 'raw_html_div.txt', 'Shanghai Schedule.csv'
rows = [['Carrier', 'Name', 'Voyage', 'ETA', 'ETB', 'ETD']]
soup = BeautifulSoup(pathlib.Path('raw_html_div.txt').read_text(encoding='utf-8'), 'lxml')

for block in soup.select('.pYplGY'):
    carrier = block.select_one('.IUKudo').get_text(strip=True)
    for row in block.select('.u3xCoJ'):
        rows.append([carrier, *[s.get_text(strip=True) for s in row.select('.rVqe2J')[:5]]])

with open(OUTPUT, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerows(rows)

print(f'已生成 {len(rows)} 条记录 -> {OUTPUT}')
"""

