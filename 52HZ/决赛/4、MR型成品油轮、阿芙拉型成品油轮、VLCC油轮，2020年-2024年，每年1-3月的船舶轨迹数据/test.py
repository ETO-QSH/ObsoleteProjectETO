#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AIS RGB 像素测试（2020–2024）
- 每年一张 3600×1800 图
- MR → R=255, VLCC → G=255, AFRAMAX → B=255
- 无模糊，无归一化，仅标记存在性
"""
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
from PIL import Image

# ---------------- 配置 ----------------
AIS_ROOT = Path(
    r"D:\Desktop\Desktop\52HZ\4、MR型成品油轮、阿芙拉型成品油轮、VLCC油轮，2020年-2024年，每年1-3月的船舶轨迹数据"
)
OUT_DIR = Path("test_output")
OUT_DIR.mkdir(exist_ok=True)

SHIP_MAP = {
    "MR型成品油轮": ("MR", 0),      # (英文名, RGB通道索引)
    "VLCC油轮": ("VLCC", 1),
    "阿芙拉型成品油轮": ("AFRAMAX", 2)
}
YEARS = ["2020", "2021", "2022", "2023", "2024"]

# 网格参数
GRID_RES = 0.1
LON_MIN, LON_MAX = -180.0, 180.0
LAT_MIN, LAT_MAX = -90.0, 90.0
nx = int((LON_MAX - LON_MIN) / GRID_RES)  # 3600
ny = int((LAT_MAX - LAT_MIN) / GRID_RES)  # 1800

# ---------------- 主循环 ----------------
for year in YEARS:
    print(f"\nProcessing {year} ...")
    # 初始化 RGB 图 (H, W, C) = (1800, 3600, 3)
    rgb_img = np.zeros((ny, nx, 3), dtype=np.uint8)

    for dir_zh, (ship_eng, channel) in SHIP_MAP.items():
        csv_file = AIS_ROOT / dir_zh / f"{ship_eng}_{year}.csv"
        if not csv_file.exists():
            print(f"  Skip {ship_eng}: file not found")
            continue

        # 读取并转换 CRS
        df = pd.read_csv(csv_file)[["longitude", "latitude"]].dropna()
        gdf = gpd.GeoDataFrame(
            df,
            geometry=gpd.points_from_xy(df.longitude, df.latitude),
            crs="EPSG:3857"
        )
        gdf = gdf.to_crs("EPSG:4326")
        lons = gdf.geometry.x.values
        lats = gdf.geometry.y.values

        print(f"  Loaded {len(lons)} raw points for {ship_eng}")

        # 过滤有效点
        valid = (
            (lons >= LON_MIN) & (lons < LON_MAX) &
            (lats >= LAT_MIN) & (lats <= LAT_MAX) &
            np.isfinite(lons) & np.isfinite(lats) &
            (lats > -85.0) & (lats < 85.0) &           # 排除极地
            ~((lats == 0.0) & (lons == 0.0))           # 排除 (0,0)
        )
        lons, lats = lons[valid], lats[valid]
        print(f"    After filtering: {len(lons)} points")

        if len(lons) == 0:
            continue

        # 量化到 0.1° 网格
        lons = np.round(lons / GRID_RES) * GRID_RES
        lats = np.round(lats / GRID_RES) * GRID_RES

        # 转像素索引
        i_arr = ((lons - LON_MIN) / GRID_RES).astype(int)
        j_arr = ((lats - LAT_MIN) / GRID_RES).astype(int)

        # 边界检查
        valid_idx = (i_arr >= 0) & (i_arr < nx) & (j_arr >= 0) & (j_arr < ny)
        i_arr, j_arr = i_arr[valid_idx], j_arr[valid_idx]

        # 标记该通道为 255（有船即亮）
        rgb_img[j_arr, i_arr, channel] = 255

    # 保存图像
    output_path = OUT_DIR / f"test_rgb_{year}.png"
    img_pil = Image.fromarray(rgb_img, mode='RGB')
    img_pil.save(output_path)
    print(f"  Saved: {output_path} (size: {nx}x{ny})")

print("\n✅ All done! Check 'test_output' folder.")
