#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
全球 AIS 0.1° 像素热力图（双输出：纯热力图 + 带坐标图）
- 纯图：严格 3600×1800
- 带坐标图：热力图区域对齐 3600×1800，整体图像含标签
"""
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from scipy.ndimage import convolve
from PIL import Image

# ---------------- 常量 ----------------
AIS_ROOT = Path(
    r"D:\Desktop\Desktop\52HZ\4、MR型成品油轮、阿芙拉型成品油轮、VLCC油轮，2020年-2024年，每年1-3月的船舶轨迹数据"
)
OUT_DIR = Path("output")
OUT_DIR.mkdir(exist_ok=True)

SHIP_MAP = {"MR型成品油轮": "MR", "VLCC油轮": "VLCC", "阿芙拉型成品油轮": "AFRAMAX"}
COLOR_SCALE = {"MR": (1, 0, 0), "VLCC": (0, 1, 0), "AFRAMAX": (0, 0, 1)}
YEARS = [str(y) for y in range(2020, 2025)]

# 全球 0.1° 网格
GRID_RES = 0.1
LON_MIN, LON_MAX = -180.0, 180.0
LAT_MIN, LAT_MAX = -90.0, 90.0
nx = int((LON_MAX - LON_MIN) / GRID_RES)  # 3600
ny = int((LAT_MAX - LAT_MIN) / GRID_RES)  # 1800

KERNEL_5 = np.array([
    [0, 1, 1, 1, 0],
    [1, 3, 3, 3, 1],
    [1, 3, 5, 3, 1],
    [1, 3, 3, 3, 1],
    [0, 1, 1, 1, 0]
], dtype=np.float32)

# ---------------- 缓存与数据加载（已修复 CRS）----------------
CACHE = AIS_ROOT / "data_cache"
CACHE.mkdir(exist_ok=True)


def get_ais(dir_zh: str, year: str) -> gpd.GeoDataFrame:
    names = {"MR型成品油轮": "MR", "VLCC油轮": "VLCC", "阿芙拉型成品油轮": "AFRAMAX"}
    ship_eng = names[dir_zh]
    csv_file = AIS_ROOT / dir_zh / f"{ship_eng}_{year}.csv"
    pq_file = CACHE / f"{ship_eng}_{year}.parquet"

    if pq_file.exists():
        return gpd.read_parquet(pq_file)

    if not csv_file.exists():
        raise FileNotFoundError(f"File not found: {csv_file}")

    df = pd.read_csv(csv_file)[["longitude", "latitude"]].dropna()

    # 假设原始数据是 EPSG:3857（Web Mercator）
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df.longitude, df.latitude),
        crs="EPSG:3857"
    )
    gdf = gdf.to_crs("EPSG:4326")  # 转为经纬度
    gdf.to_parquet(pq_file, index=False)
    return gdf


# ---------------- 主循环 ----------------
for year in YEARS:
    print(f"Processing {year} ...")
    density_maps = {
        "MR": np.zeros((ny, nx), dtype=np.float32),
        "VLCC": np.zeros((ny, nx), dtype=np.float32),
        "AFRAMAX": np.zeros((ny, nx), dtype=np.float32),
    }

    # 构建密度图
    for dir_zh, ship in SHIP_MAP.items():
        try:
            gdf = get_ais(dir_zh, year)
            print(f"  Loaded {len(gdf)} points for {ship}")
        except FileNotFoundError as e:
            print(f"  Skip {ship}: {e}")
            continue

        lons = gdf.geometry.x.values
        lats = gdf.geometry.y.values
        print("lons:", lons, "\n", "lats:", lats)
        print(f"lon: [{lons.min():.1f}, {lons.max():.1f}], lat: [{lats.min():.1f}, {lats.max():.1f}]")

        # 过滤有效经纬度
        valid = (
                (lons >= LON_MIN) & (lons < LON_MAX) &
                (lats >= LAT_MIN) & (lats <= LAT_MAX) &
                np.isfinite(lons) & np.isfinite(lats)
        )
        lons, lats = lons[valid], lats[valid]
        if len(lons) == 0:
            continue

        lons = np.round(lons / 0.1) * 0.1
        lats = np.round(lats / 0.1) * 0.1

        valid = (lons >= LON_MIN) & (lons < LON_MAX) & (lats >= LAT_MIN) & (lats <= LAT_MAX)
        lons, lats = lons[valid], lats[valid]
        if len(lons) == 0:
            continue

        # 转索引（现在必为整数）
        i_arr = ((lons - LON_MIN) / GRID_RES).astype(int)
        j_arr = ((lats - LAT_MIN) / GRID_RES).astype(int)

        # 索引范围检查（应全合法，但保留防御）
        valid_idx = (i_arr >= 0) & (i_arr < nx) & (j_arr >= 0) & (j_arr < ny)
        i_arr, j_arr = i_arr[valid_idx], j_arr[valid_idx]

        np.add.at(density_maps[ship], (j_arr, i_arr), 1)

    # 卷积模糊
    blurred_maps = {}
    for ship in density_maps:
        blurred_maps[ship] = convolve(density_maps[ship], KERNEL_5, mode='constant', cval=0.0)

    # 合成 RGB
    rgb_stack = np.zeros((ny, nx, 3), dtype=np.float32)
    for idx, ship in enumerate(["MR", "VLCC", "AFRAMAX"]):
        rgb_stack[:, :, idx] = blurred_maps[ship] * COLOR_SCALE[ship][idx]

    # 合成 RGB（保持原始强度）
    rgb_stack = np.zeros((ny, nx, 3), dtype=np.float32)
    for idx, ship in enumerate(["MR", "VLCC", "AFRAMAX"]):
        rgb_stack[:, :, idx] = blurred_maps[ship] * COLOR_SCALE[ship][idx]

    # 仅防负值（理论上不会负，但保险）
    rgb_stack = np.clip(rgb_stack, 0, None)

    # ==============================
    # 1. 保存纯热力图：无归一化，仅防溢出 255
    # ==============================
    img_array = np.clip(rgb_stack, 0, 255).astype(np.uint8)  # ←←← 核心：只 clip 到 255
    img_pil = Image.fromarray(img_array, mode='RGB')
    raw_path = OUT_DIR / f"heatmap_raw_{year}.png"
    img_pil.save(raw_path)

    # ==============================
    # 2. 保存 cartopy 图：同样不归一化，但 matplotlib 需要 [0,1] → 所以除以 255.0
    # ==============================
    # 注意：imshow 要求 float 图像在 [0,1]，所以我们传 rgb_stack/255.0
    rgb_for_plot = np.clip(rgb_stack / 255.0, 0, 1)

    fig = plt.figure(figsize=(36, 18), dpi=100)
    ax = fig.add_subplot(111, projection=ccrs.PlateCarree())
    ax.set_extent([LON_MIN, LON_MAX, LAT_MIN, LAT_MAX], crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.LAND.with_scale('110m'), color='0.85')
    ax.add_feature(cfeature.OCEAN.with_scale('110m'), color='0.95')
    ax.add_feature(cfeature.COASTLINE.with_scale('110m'), linewidth=0.2, color='0.3')

    ax.imshow(
        rgb_for_plot,
        origin='lower',
        extent=[LON_MIN, LON_MAX, LAT_MIN, LAT_MAX],
        transform=ccrs.PlateCarree(),
        interpolation='none',
        zorder=10,
        alpha=0.85
    )

    # 网格线
    gl = ax.gridlines(draw_labels=True, linewidth=0.3, color='0.4', alpha=0.5)
    gl.top_labels = False
    gl.right_labels = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER

    ax.set_title(f"Global AIS Heatmap ({year})", fontsize=20, pad=20)

    cartopy_path = OUT_DIR / f"heatmap_cartopy_{year}.png"
    # 保存时不裁剪，保留完整 3600×1800 热力图区域
    fig.savefig(
        cartopy_path,
        dpi=100,
        bbox_inches='tight',  # 允许包含标签
        pad_inches=0.1,  # 少量内边距
        facecolor='white'
    )
    plt.close(fig)
    print(f"Saved cartopy map: {cartopy_path} (heatmap area = 3600×1800)")

print("All done!")
