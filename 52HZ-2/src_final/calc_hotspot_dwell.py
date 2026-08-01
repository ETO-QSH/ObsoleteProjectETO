"""
脚本6: 高风险区域驻留指标（预留）
===================================
预期输入: 决赛资料/重点港口与锚地坐标.geojson (或 .csv)
  包含: 受制裁国家关键港口 + STS 转运热点区域坐标
辅助:   ais_clean_2026.parquet
输出:   output_final/hotspot_dwell.csv
  列: mmsi, hotspot_dwell_hours, hotspot_dwell_ratio, sts_dwell_hours, sts_dwell_ratio

逻辑:
  1. 加载高风险区域多边形（制裁国港口 + STS 热点）
  2. 计算每艘船在高风险区域内的停留时长
  3. 占其总观测时长的比例

目前赛方数据尚未提供，脚本框架已就绪。
"""

import pandas as pd
import numpy as np
import geopandas as gpd
from pathlib import Path
from shapely import prepared

ROOT = Path(__file__).parent.parent
INPUT_PATH = ROOT / "决赛资料" / "重点港口与锚地坐标.geojson"
PARQUET_CLEAN = ROOT / "database" / "ais_clean_2026.parquet"
OUTPUT_PATH = ROOT / "output_final" / "hotspot_dwell.csv"


def load_hotspots(input_path: Path, label: str):
    """加载高风险区域，返回 prepared geometry"""
    if input_path.suffix == '.geojson' or input_path.suffix == '.json':
        gdf = gpd.read_file(input_path)
    elif input_path.suffix == '.csv':
        df = pd.read_csv(input_path)
        # 预期有 lat, lon, radius_km 列
        from shapely.geometry import Point
        geoms = [Point(r['lon'], r['lat']) for _, r in df.iterrows()]
        gdf = gpd.GeoDataFrame(geometry=geoms, crs="EPSG:4326")
        if 'radius_km' in df.columns:
            gdf = gdf.to_crs("EPSG:3857")
            gdf.geometry = gdf.geometry.buffer(df['radius_km'].values * 1000)
            gdf = gdf.to_crs("EPSG:4326")
    else:
        raise ValueError(f"不支持的文件格式: {input_path.suffix}")

    union = gdf.geometry.union_all()
    prep = prepared.prep(union)
    print(f"  {label}: {len(gdf)} 个区域, union 完成")
    return prep


def process() -> pd.DataFrame:
    """计算高风险区域驻留指标（框架）"""
    # ---- 1. 加载高风险区域 ----
    if not INPUT_PATH.exists():
        print("[热点] 数据文件未提供，跳过")
        return pd.DataFrame(columns=["mmsi", "hotspot_dwell_hours",
                                     "hotspot_dwell_ratio"])

    # 尝试分别加载 STS 热点和制裁港口
    # TODO: 根据赛方实际文件结构调整
    hotspot = load_hotspots(INPUT_PATH, "高风险区域")

    # ---- 2. 逐船计算驻留时长 ----
    # 读取 ais_clean，对每艘船统计在 hotspot 内的时长
    # 框架留空，数据到后填充

    return pd.DataFrame(columns=["mmsi", "hotspot_dwell_hours",
                                 "hotspot_dwell_ratio"])


if __name__ == "__main__":
    print("=" * 60)
    print("高风险区域驻留指标")
    print("=" * 60)

    if INPUT_PATH.exists():
        df = process()
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
        print(f"[输出] {OUTPUT_PATH}")
    else:
        print(f"\n[等待] 数据文件尚未提供: {INPUT_PATH}")
        print(f"  预期格式: GeoJSON (多边形) 或 CSV (lat, lon, radius_km)")
        print(f"  数据到后直接运行本脚本即可")
