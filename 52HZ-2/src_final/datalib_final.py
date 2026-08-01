"""
决赛数据基础设施：影子船队识别
=================================
AIS 动态数据 (7列 CSV) → Parquet 缓存
船舶档案加载
港口清单加载

适配决赛数据格式（仅 AFRAMAX + 船龄>15 年）：
- 动态数据列: mmsi, acqtime, cog, latitude, longitude, speed, true_head
- 坐标/速度/航向转换规则与复赛一致
"""

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import geopandas as gpd

from pathlib import Path
from functools import lru_cache

# ============================================================
# 路径配置
# ============================================================
ROOT = Path(__file__).parent.parent
AIS_DIR = ROOT / "决赛资料" / "AIS数据" / "动态数据"
ARCHIVE_DIR = ROOT / "决赛资料" / "船舶档案"
PORT_LIST_DIR = ROOT / "决赛资料" / "原油装卸港清单"
CACHE = ROOT / "database"
CACHE.mkdir(parents=True, exist_ok=True)

# ============================================================
# 动态数据列定义（决赛 7 列格式）
# ============================================================
DYNAMIC_COLS = [
    "mmsi", "acqtime", "cog", "latitude", "longitude", "speed", "true_head"
]

# Parquet schema（全部转换后的列）
PA_SCHEMA = pa.schema([
    ("mmsi", pa.int64()),
    ("acqtime", pa.timestamp('ns', tz='UTC')),
    ("longitude", pa.float64()),
    ("latitude", pa.float64()),
    ("speed_knots", pa.float64()),
    ("speed_ms", pa.float64()),
    ("cog_deg", pa.float64()),
    ("heading_deg", pa.float64()),
    ("month", pa.int32()),           # 202601 ~ 202606
    ("date", pa.timestamp('ns')),
])

PD_DTYPE = {
    "mmsi": "int64",
    "acqtime": "int64",
    "cog": "int64",
    "latitude": "int64",
    "longitude": "int64",
    "speed": "int64",
    "true_head": "int64",
}

CHUNK_SIZE = 500_000

# ============================================================
# 核心：CSV → Parquet
# ============================================================

def build_ais_parquet() -> Path:
    """
    将 2026 年 1-6 月所有 CSV 转为单个 Parquet 文件。
    缓存路径：database/ais_final_2026.parquet
    """
    pq_path = CACHE / "ais_final_2026.parquet"
    if pq_path.exists():
        print(f"[缓存] {pq_path} 已存在，跳过构建")
        return pq_path

    if not AIS_DIR.exists():
        raise FileNotFoundError(f"AIS 数据目录不存在: {AIS_DIR}")

    csv_files = sorted(AIS_DIR.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"在 {AIS_DIR} 中未找到 CSV 文件")

    print(f"发现 {len(csv_files)} 个 CSV 文件，开始构建 {pq_path.name}...")

    writer = None
    total_rows = 0

    for csv_path in csv_files:
        # 从文件名提取年月，如 "202601_AFRAMAX_age15.csv" → 202601
        month_str = csv_path.stem.split("_")[0]
        try:
            month = int(month_str)
            year = month // 100
            mon = month % 100
            # 月份中位日期作为 date 列
            base_date = pd.Timestamp(year=year, month=mon, day=15)
        except (ValueError, IndexError):
            print(f"  警告: 无法从文件名解析月份 {csv_path.name}，跳过")
            continue

        print(f"\n[处理] {csv_path.name} | month={month}")

        chunk_iter = pd.read_csv(
            csv_path,
            dtype=PD_DTYPE,
            chunksize=CHUNK_SIZE,
            low_memory=False,
        )

        chunk_count = 0
        for chunk in chunk_iter:
            # 坐标转换
            chunk["longitude"] = chunk["longitude"].astype("float64") / 1_000_000
            chunk["latitude"] = chunk["latitude"].astype("float64") / 1_000_000
            # 速度转换：原始单位 1/10 节
            chunk["speed_knots"] = chunk["speed"].astype("float64") / 10
            chunk["speed_ms"] = chunk["speed_knots"] * 0.514444
            # 角度转换：原始单位 1/100 度
            chunk["cog_deg"] = chunk["cog"].astype("float64") / 100
            chunk["heading_deg"] = chunk["true_head"].astype("float64") / 100
            # 时间戳转换
            chunk["acqtime"] = pd.to_datetime(chunk["acqtime"], unit='s', utc=True)
            # 元数据
            chunk["month"] = month
            chunk["date"] = base_date

            # 只保留需要的列
            keep_cols = [
                "mmsi", "acqtime", "longitude", "latitude",
                "speed_knots", "speed_ms", "cog_deg", "heading_deg",
                "month", "date"
            ]
            chunk = chunk[keep_cols]

            table = pa.Table.from_pandas(chunk, schema=PA_SCHEMA)

            if writer is None:
                writer = pq.ParquetWriter(pq_path, PA_SCHEMA, compression="zstd")
            writer.write_table(table)

            total_rows += len(chunk)
            chunk_count += 1
            del chunk, table

        print(f"  -> 块数: {chunk_count} | 累计: {total_rows:>12,} 行")

    if writer:
        writer.close()

    print(f"\n[完成] 总行数: {total_rows:,} → {pq_path} ({pq_path.stat().st_size / 1024**3:.1f} GB)")
    return pq_path


# ============================================================
# 动态数据读取接口
# ============================================================

def get_ais_dynamic(
    columns: list[str] = None,
    date_start: str = None,
    date_end: str = None,
    mmsi_list: list[int] = None,
    bbox: tuple = None,
    months: list[int] = None,
    limit: int = None,
) -> gpd.GeoDataFrame:
    """
    读取 AIS 动态数据，支持多条件过滤。

    Parameters
    ----------
    columns : 需要的列，默认全部
    date_start / date_end : 日期范围，如 "2026-03-01"
    mmsi_list : MMSI 列表过滤
    bbox : (min_lon, min_lat, max_lon, max_lat)
    months : 月份列表，如 [202603, 202604]
    limit : 最大返回行数
    """
    pq_path = build_ais_parquet()

    default_cols = [
        "mmsi", "acqtime", "longitude", "latitude",
        "speed_knots", "speed_ms", "cog_deg", "heading_deg",
        "month", "date"
    ]
    user_columns = columns or default_cols

    # 确保过滤列在读取列中
    read_columns = set(user_columns)
    if date_start or date_end:
        read_columns.add("acqtime")
    if mmsi_list:
        read_columns.add("mmsi")
    if bbox:
        read_columns.update(["longitude", "latitude"])
    if months:
        read_columns.add("month")
    read_columns.update(["longitude", "latitude"])  # geometry 必需
    read_columns = list(read_columns)

    pf = pq.ParquetFile(pq_path)
    batches = []
    total_rows = 0
    batch_size = 200_000

    for batch in pf.iter_batches(batch_size=batch_size, columns=read_columns):
        df = batch.to_pandas()

        mask = pd.Series(True, index=df.index)
        if date_start:
            mask &= df["acqtime"] >= pd.Timestamp(date_start)
        if date_end:
            mask &= df["acqtime"] <= pd.Timestamp(date_end)
        if mmsi_list:
            mask &= df["mmsi"].isin(mmsi_list)
        if bbox:
            min_lon, min_lat, max_lon, max_lat = bbox
            mask &= (df["longitude"] >= min_lon) & (df["longitude"] <= max_lon)
            mask &= (df["latitude"] >= min_lat) & (df["latitude"] <= max_lat)
        if months:
            mask &= df["month"].isin(months)

        filtered = df[mask]
        if len(filtered) > 0:
            # 始终保留 geometry 必需的列
            keep_cols = [c for c in user_columns if c in filtered.columns]
            for geo_col in ["longitude", "latitude"]:
                if geo_col not in keep_cols and geo_col in filtered.columns:
                    keep_cols.append(geo_col)
            batches.append(filtered[keep_cols])
            total_rows += len(filtered)

        if limit and total_rows >= limit:
            break

        del df, batch

    if not batches:
        empty = pd.DataFrame(columns=user_columns)
        return gpd.GeoDataFrame(empty, geometry=[], crs="EPSG:4326")

    df = pd.concat(batches, ignore_index=True)
    if limit:
        df = df.head(limit)

    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df.longitude, df.latitude),
        crs="EPSG:4326"
    )
    return gdf


def get_ais_dynamic_iter(
    columns: list[str] = None,
    date_start: str = None,
    date_end: str = None,
    mmsi_list: list[int] = None,
    bbox: tuple = None,
    months: list[int] = None,
    batch_size: int = 200_000,
):
    """
    迭代器版：逐批返回 GeoDataFrame，适合全量扫描。
    """
    pq_path = build_ais_parquet()

    default_cols = [
        "mmsi", "acqtime", "longitude", "latitude",
        "speed_knots", "speed_ms", "cog_deg", "heading_deg",
        "month", "date"
    ]
    user_columns = columns or default_cols

    read_columns = set(user_columns)
    if date_start or date_end:
        read_columns.add("acqtime")
    if mmsi_list:
        read_columns.add("mmsi")
    if bbox:
        read_columns.update(["longitude", "latitude"])
    if months:
        read_columns.add("month")
    read_columns.update(["longitude", "latitude"])
    read_columns = list(read_columns)

    pf = pq.ParquetFile(pq_path)

    for batch in pf.iter_batches(batch_size=batch_size, columns=read_columns):
        df = batch.to_pandas()

        mask = pd.Series(True, index=df.index)
        if date_start:
            mask &= df["acqtime"] >= pd.Timestamp(date_start)
        if date_end:
            mask &= df["acqtime"] <= pd.Timestamp(date_end)
        if mmsi_list:
            mask &= df["mmsi"].isin(mmsi_list)
        if bbox:
            min_lon, min_lat, max_lon, max_lat = bbox
            mask &= (df["longitude"] >= min_lon) & (df["longitude"] <= max_lon)
            mask &= (df["latitude"] >= min_lat) & (df["latitude"] <= max_lat)
        if months:
            mask &= df["month"].isin(months)

        filtered = df[mask]
        if len(filtered) == 0:
            del df, batch
            continue

        keep_cols = [c for c in user_columns if c in filtered.columns]
        for geo_col in ["longitude", "latitude"]:
            if geo_col not in keep_cols and geo_col in filtered.columns:
                keep_cols.append(geo_col)
        filtered = filtered[keep_cols]

        gdf = gpd.GeoDataFrame(
            filtered,
            geometry=gpd.points_from_xy(filtered.longitude, filtered.latitude),
            crs="EPSG:4326"
        )
        yield gdf
        del df, batch, gdf


# ============================================================
# 船舶档案
# ============================================================

class ShipArchive:
    """船舶档案查询类（按 MMSI 快速查询）"""

    def __init__(self, csv_path: Path):
        self.csv_path = csv_path
        df = pd.read_csv(csv_path, low_memory=False)
        # 统一 MMSI 列名和类型
        if "ship_mmsi" in df.columns:
            df["ship_mmsi"] = (
                df["ship_mmsi"]
                .astype(str).str.strip().str.strip('"').str.strip("'")
            )
            df["ship_mmsi"] = pd.to_numeric(df["ship_mmsi"], errors="coerce").astype("Int64")
        self._df = df
        self._by_mmsi = {}
        for _, row in df.iterrows():
            m = row["ship_mmsi"]
            if pd.notna(m):
                self._by_mmsi[int(m)] = row

    def get_by_mmsi(self, mmsi: int):
        """查询单条档案，返回 pd.Series 或 None"""
        return self._by_mmsi.get(mmsi)

    def get_by_mmsi_list(self, mmsi_list: list[int]) -> pd.DataFrame:
        """批量查询"""
        rows = [self._by_mmsi[m] for m in mmsi_list if m in self._by_mmsi]
        if not rows:
            return pd.DataFrame(columns=self._df.columns)
        return pd.DataFrame(rows)

    def get_mmsi_set(self) -> set[int]:
        """返回所有 MMSI 集合"""
        return set(self._by_mmsi.keys())

    def __len__(self):
        return len(self._by_mmsi)

    def __repr__(self):
        return f"ShipArchive({self.csv_path.name}, {len(self)} ships, {len(self._df.columns)} cols)"


@lru_cache(maxsize=1)
def get_ship_archive() -> ShipArchive:
    """加载船舶档案（带缓存）"""
    csv_path = ARCHIVE_DIR / "AFRAMAX_age15_20260724.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"船舶档案不存在: {csv_path}")
    return ShipArchive(csv_path)


# ============================================================
# 港口清单
# ============================================================

@lru_cache(maxsize=1)
def get_port_lists() -> dict[str, pd.DataFrame]:
    """
    加载装货港/卸货港清单。
    返回 {"load": DataFrame, "discharge": DataFrame}
    """
    result = {}
    load_path = PORT_LIST_DIR / "原油相关货物装货港清单.xlsx"
    discharge_path = PORT_LIST_DIR / "原油相关货物卸货港清单.xlsx"

    if load_path.exists():
        df_load = pd.read_excel(load_path)
        # 列名标准化
        df_load.columns = ["country", "port"]
        result["load"] = df_load
        print(f"[港口清单] 装货港: {len(df_load)} 条")

    if discharge_path.exists():
        df_discharge = pd.read_excel(discharge_path)
        df_discharge.columns = ["country", "port"]
        result["discharge"] = df_discharge
        print(f"[港口清单] 卸货港: {len(df_discharge)} 条")

    return result


# ============================================================
# 便捷函数：获取全部 MMSI 列表
# ============================================================

@lru_cache(maxsize=1)
def get_all_mmsi() -> list[int]:
    """从 Parquet 中提取全部不重复 MMSI"""
    pq_path = build_ais_parquet()
    pf = pq.ParquetFile(pq_path)
    mmsi_set = set()
    for batch in pf.iter_batches(batch_size=500_000, columns=["mmsi"]):
        df = batch.to_pandas()
        mmsi_set.update(df["mmsi"].unique())
        del df
    return sorted(mmsi_set)


# ============================================================
# 便捷函数：单船轨迹提取
# ============================================================

def get_vessel_trajectory(mmsi: int, months: list[int] = None) -> gpd.GeoDataFrame:
    """
    提取单艘船的全部轨迹，按时间排序。
    months: 指定月份，默认全部6个月
    """
    return get_ais_dynamic(
        mmsi_list=[mmsi],
        months=months,
        columns=["mmsi", "acqtime", "longitude", "latitude",
                 "speed_knots", "cog_deg", "heading_deg", "month"]
    ).sort_values("acqtime")


# ============================================================
# 主程序
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("决赛 AIS 数据基础设施构建")
    print(f"缓存目录: {CACHE}")
    print("=" * 60)

    # --- 1. 构建 Parquet ---
    print("\n>>> 构建 AIS Parquet...")
    pq_path = build_ais_parquet()

    # --- 2. 加载船舶档案 ---
    print("\n>>> 加载船舶档案...")
    archive = get_ship_archive()
    print(f"  {archive}")

    # --- 3. 加载港口清单 ---
    print("\n>>> 加载港口清单...")
    ports = get_port_lists()

    # --- 4. 验证：读取 3 月前 10000 条 ---
    print("\n>>> 验证读取（2026年3月，limit=10000）...")
    gdf = get_ais_dynamic(months=[202603], limit=10000)
    print(f"  行数: {len(gdf):,}")
    print(f"  列: {list(gdf.columns)}")
    print(f"  MMSI 数: {gdf['mmsi'].nunique()}")
    print(gdf.head(3))

    # --- 5. 统计概况 ---
    print("\n>>> 数据概况...")
    print(f"  全部 MMSI 数: {len(get_all_mmsi()):,}")
    for m in [202601, 202602, 202603, 202604, 202605, 202606]:
        gdf = get_ais_dynamic(months=[m], columns=["mmsi"], limit=1_000_000)
        print(f"  month={m}: 抽样 {len(gdf):,} 行")

    print("\n" + "=" * 60)
    print("全部完成")
