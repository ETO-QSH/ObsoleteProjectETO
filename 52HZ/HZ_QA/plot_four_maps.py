import math
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

from pathlib import Path
from cartopy import crs, feature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

from database.datalib import get_ais, get_ships
from config import CORRIDOR_GEOJSON, CELL_M, log, safe_exit

# ---------- 参数 ----------
log("开始初始化参数")

DPI = 100
W, H = 640, 720
HEATMAP_SIZE = 480

CRS_MAP = crs.PlateCarree()
CELL_KM = CELL_M / 1000
OUT_DIR = Path("output")
OUT_DIR.mkdir(exist_ok=True)

plt.rcParams['font.sans-serif'] = ['Lolita']

# ---------- 1. 数据 ----------
log("开始进行数据收集")

# 读取corridor底图
corridor = gpd.read_file(CORRIDOR_GEOJSON).to_crs('EPSG:4326')
lon_min, lat_min, lon_max, lat_max = map(round, corridor.total_bounds)

# 读取ais数据
ais = get_ais()

# 数据范围裁剪
ais = ais[
    (ais['latitude'] >= lat_min) & (ais['latitude'] <= lat_max) &
    (ais['longitude'] >= lon_min) & (ais['longitude'] <= lon_max)
]

# 以122E, 31N为标准计算每度的长度
ref_lat = (lat_min + lat_max) / 2
ref_lon = (lon_min + lon_max) / 2
earth_radius = 6378137  # WGS84

# 1度(经|纬)在该位置的米数
cell_lon_deg = CELL_M / (math.cos(math.radians(ref_lat)) * 2 * math.pi * earth_radius / 360)
cell_lat_deg = CELL_M / (2 * math.pi * earth_radius / 360)

gdf = ais.to_crs('EPSG:4326')
gdf = gpd.sjoin(gdf, corridor, predicate='within')

# 检查空间连接后是否有数据
if gdf.empty:
    log("空间连接后无数据，无法绘图。请检查AIS数据和航道范围。")
    safe_exit(1)

# 栅格化（直接用网格坐标，统计时就聚合到规则网格，避免后续转换）
gx0 = int(lon_min // cell_lon_deg)
gy0 = int(lat_min // cell_lat_deg)

# 计算每条AIS的网格索引（gx, gy），直接用规则网格
gdf = ais.to_crs('EPSG:4326')
gdf = gpd.sjoin(gdf, corridor, predicate='within')
gdf['gx'] = ((gdf.geometry.x - lon_min) / cell_lon_deg).astype(int)
gdf['gy'] = ((gdf.geometry.y - lat_min) / cell_lat_deg).astype(int)

# 检查gx/gy是否有效
if gdf['gx'].isnull().all() or gdf['gy'].isnull().all() or len(gdf['gx'].dropna()) == 0:
    log("栅格化后无有效gx/gy数据，无法绘图。请检查CELL_M参数和AIS数据。")
    safe_exit(1)

# 静态船表（切为ship_mmsi索引）
ships = get_ships()
if ships.index.name != 'ship_mmsi':
    ships = ships.set_index('ship_mmsi')

# ---------- 2. 计算 ----------
log("开始进行数值计算")

# 1. 密度 ρ
rho = (
    gdf.groupby(['gx', 'gy'])['mmsi']
    .nunique()
    .reset_index(name='rho')
)
log("计算 - 密度 ρ - 完成")

# 2. 冲突 C（采样后广播）
MAX_PER_CELL = 500  # 每栅格最多 500 条
conflicts = []

for (gx, gy), grp in gdf.groupby(['gx', 'gy']):
    if len(grp) < 2:
        continue

    # 随机采样，保证可重复
    if len(grp) > MAX_PER_CELL:
        grp = grp.sample(MAX_PER_CELL, random_state=42)
    cog = grp['cog'].to_numpy()

    # 广播计算两两差值
    diff = np.abs(cog[:, None] - cog[None, :])
    mask = diff > 45
    n_conflict = np.triu(mask, 1).sum()  # 只取上三角
    conflicts.append({'gx': gx, 'gy': gy, 'C': int(n_conflict)})

C = pd.DataFrame(conflicts)
log("计算 - 冲突 C - 完成")

"""
# 2. 冲突 C（时空加权版  ps: 测试不会报错，但是我八年前的轻薄本带不动，main.py里面需要也可以相应替换）
MAX_PER_CELL = 500          # 单栅格最多 500 条
EPS = 0.1                   # km，避免除零

conflicts = []
for (gx, gy), grp in gdf.groupby(['gx', 'gy']):
    if len(grp) < 2:
        continue

    # 随机采样，保证可重复
    if len(grp) > MAX_PER_CELL:
        grp = grp.sample(MAX_PER_CELL, random_state=42)

    cog = grp['cog'].to_numpy()
    lon = grp['longitude'].to_numpy()
    lat = grp['latitude'].to_numpy()
    n = len(grp)

    # 航向差矩阵（°）
    d_cog = np.abs(cog[:, None] - cog[None, :])
    d_cog = np.minimum(d_cog, 360 - d_cog)
    mask_dir = d_cog > 45

    # 距离矩阵（km）
    dist = np.array(
        [[geodesic((lat[i], lon[i]), (lat[j], lon[j])).km for j in range(n)] for i in range(n)]
    )

    w_ij = 1 / (dist + EPS)
    w_ij = np.triu(w_ij, 1)  # 去上三角

    # 时空加权冲突量
    conflict_score = np.sum(w_ij * mask_dir)
    conflicts.append({'gx': gx, 'gy': gy, 'C': float(conflict_score)})

C = pd.DataFrame(conflicts)
log("计算 - 冲突 C - 完成")
"""

# 3. 航速
speed = (
    gdf.groupby(['gx', 'gy'])['speed']
    .mean()
)
log("计算 - 航速 s - 完成")

# 4. 船型（用 TEU 代表运力）
teu_extract = (
    ships['ship_size']
    .astype(str)
    .str.extract(r'([\d,]+)\s*(?:TEU|CEU)', expand=False)  # 同时匹配 TEU 或 CEU
    .str.replace(',', '', regex=False)
    .astype(float)
    .fillna(0)  # 无 TEU 的填 0
    .astype(int)
)
# 从 ships 提取数字并转 int
ships = ships.assign(teu=teu_extract)

gdf = gdf.merge(ships[['teu']], left_on='mmsi', right_index=True)
teu = (
    gdf.groupby(['gx', 'gy'])['teu']
    .sum()
)
log("计算 - 运力 T - 完成")

# ---------- 3. 绘图 ----------
log("开始进行图表绘制")

# 统一网格
nx = 1 + int((lon_max - lon_min) / cell_lon_deg)
ny = 1 + int((lat_max - lat_min) / cell_lat_deg)

# 检查防止nx/ny为NaN或<=0
if pd.isna(nx) or pd.isna(ny) or nx <= 1 or ny <= 1:
    log(f"网格范围异常：nx={nx}, ny={ny}，请检查AIS数据、CELL_M参数和空间范围。")
    safe_exit(1)

# 与 grid 维度一致的经纬度坐标
lons = np.linspace(lon_min, lon_max, nx)
lats = np.linspace(lat_min, lat_max, ny)

files = ['rho', 'C', 'speed', 'teu']
titles = ['船舶密度', '航迹冲突', '平均航速', '运力分布']
grids = [rho, C, speed, teu]

for f, title, df in zip(files, titles, grids):
    fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI)

    left, bottom = (W - HEATMAP_SIZE) / 2 / W, 0.1
    width, height = HEATMAP_SIZE / W, HEATMAP_SIZE / H

    ax = fig.add_axes((left, bottom, width, height), projection=CRS_MAP)
    ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=CRS_MAP)

    # 底图
    ax.add_feature(feature.LAND.with_scale('10m'), facecolor='lightgray')
    ax.add_feature(feature.COASTLINE.with_scale('10m'))
    ax.add_feature(feature.BORDERS.with_scale('10m'), linestyle=':')

    # 判断df类型，若为Series则需reset_index转为DataFrame
    if isinstance(df, pd.Series):
        df = df.reset_index()
        # 自动设置列名为f
        df = df.rename(columns={0: f})

    grid = np.full((ny - 1, nx - 1), np.nan)
    for _, row in df.iterrows():
        ix = int(row['gx'])
        iy = int(row['gy'])
        if 0 <= iy < ny - 1 and 0 <= ix < nx - 1:
            grid[iy, ix] = row[f]

    # 热力图
    im = ax.pcolormesh(lons, lats, grid, cmap='YlOrRd', transform=CRS_MAP)

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

    log(f"已生成：{title}图")

safe_exit(0)
