import rarfile
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import geopandas as gpd

from pathlib import Path
from functools import lru_cache


# ---------- 路径配置 ----------
ROOT = Path(__file__).parent.parent

RAR_DIR = ROOT / "database" / "AIS动态数据"
STATIC_DIR = ROOT / "database" / "AIS静态数据"
ARCHIVE_DIR = ROOT / "database" / "船舶档案"

CACHE = ROOT / "database"
CACHE.mkdir(parents=True, exist_ok=True)

rarfile.UNRAR_TOOL = r"D:\Program Files\WinRAR\UnRAR.exe"


# ---------- 动态数据列定义 ----------
DYNAMIC_COLS = [
    "mmsi", "acqtime", "target_type", "data_supplier", "data_source",
    "move_status", "longitude", "latitude", "area_id", "speed",
    "conversion", "cog", "heading", "power", "imitator", "extend"
]

PA_SCHEMA = pa.schema([
    ("mmsi", pa.int64()),
    ("acqtime", pa.timestamp('ns', tz='UTC')),
    ("target_type", pa.int8()),
    ("data_supplier", pa.int8()),
    ("data_source", pa.int8()),
    ("move_status", pa.int8()),
    ("longitude", pa.float64()),
    ("latitude", pa.float64()),
    ("area_id", pa.int64()),
    ("speed", pa.int16()),
    ("conversion", pa.float32()),
    ("cog", pa.int16()),
    ("heading", pa.int16()),
    ("power", pa.float32()),
    ("imitator", pa.string()),
    ("extend", pa.string()),
    ("speed_knots", pa.float64()),
    ("speed_ms", pa.float64()),
    ("cog_deg", pa.float64()),
    ("heading_deg", pa.float64()),
    ("date", pa.timestamp('ns')),
])

PD_DTYPE = {
    "mmsi": "int64",
    "target_type": "int8",
    "data_supplier": "int8",
    "data_source": "int8",
    "move_status": "int8",
    "longitude": "float64",
    "latitude": "float64",
    "area_id": "int64",
    "speed": "int16",
    "conversion": "float32",
    "cog": "int16",
    "heading": "int16",
    "power": "float32",
    "imitator": "str",
    "extend": "str",
}

CHUNK_SIZE = 500_000


# ============================================================
#  核心：边解压 -> 分块读取 -> 转 parquet -> 删 CSV
# ============================================================


def build_ais_parquet(year: int = 25) -> Path:
    """
    边解压 RAR 边生成 parquet，按年份命名。
    year: 25 -> ais_dynamic_25.parquet (2025年)
    year: 26 -> ais_dynamic_26.parquet (2026年)
    """
    pq_path = CACHE / f"ais_dynamic_{year}.parquet"
    if pq_path.exists():
        return pq_path

    TMP_DIR = CACHE / "tmp_dir"
    TMP_DIR.mkdir(exist_ok=True)

    rar_dir = Path(RAR_DIR)
    if not rar_dir.exists():
        raise FileNotFoundError(f"RAR 目录不存在: {rar_dir}")

    all_rars = sorted(rar_dir.glob("*.rar"))
    main_volumes = []
    seen = set()
    for f in all_rars:
        stem = f.stem
        base = stem
        if ".part" in stem.lower():
            base = stem.rsplit(".", 1)[0]
        if base not in seen:
            seen.add(base)
            main_volumes.append(f)

    if not main_volumes:
        raise FileNotFoundError(f"在 {rar_dir} 中未找到 RAR 文件")

    print(f"发现 {len(main_volumes)} 个 RAR 主分卷，开始构建 ais_dynamic_{year}.parquet...")

    writer = None
    total_rows = 0

    for rar_path in main_volumes:
        print(f"\n[解压] {rar_path.name}")
        try:
            with rarfile.RarFile(rar_path, mode='r') as rf:
                for info in rf.infolist():
                    if info.is_dir():
                        continue

                    rf.extract(info, path=TMP_DIR)
                    csv_path = TMP_DIR / info.filename

                    if not csv_path.exists():
                        print(f"  警告: 文件未生成 {info.filename}")
                        continue

                    date_str = csv_path.stem.split("-")[-1]
                    try:
                        date = pd.to_datetime(date_str, format="%Y%m%d")
                    except ValueError:
                        print(f"  跳过: 日期解析失败 {csv_path.name}")
                        csv_path.unlink()
                        continue

                    chunk_iter = pd.read_csv(
                        csv_path,
                        header=None,
                        names=DYNAMIC_COLS,
                        dtype=PD_DTYPE,
                        chunksize=CHUNK_SIZE,
                        low_memory=False
                    )

                    chunk_count = 0
                    for chunk in chunk_iter:
                        chunk["acqtime"] = pd.to_datetime(chunk["acqtime"], unit='s', utc=True)
                        chunk["longitude"] = chunk["longitude"] / 1_000_000
                        chunk["latitude"] = chunk["latitude"] / 1_000_000
                        chunk["speed_knots"] = chunk["speed"] / 10
                        chunk["speed_ms"] = chunk["speed_knots"] * chunk["conversion"]
                        chunk["cog_deg"] = chunk["cog"] / 100
                        chunk["heading_deg"] = chunk["heading"] / 100
                        chunk["date"] = date

                        table = pa.Table.from_pandas(chunk, schema=PA_SCHEMA)

                        if writer is None:
                            writer = pq.ParquetWriter(pq_path, PA_SCHEMA, compression="zstd")
                        writer.write_table(table)

                        total_rows += len(chunk)
                        chunk_count += 1
                        del chunk, table

                    csv_path.unlink()
                    print(f"  -> {info.filename} | 日期: {date.date()} | 块数: {chunk_count} | 累计: {total_rows:,} 行")

        except Exception as e:
            print(f"  错误 [{rar_path.name}]: {e}")
            raise

    if writer:
        writer.close()

    try:
        TMP_DIR.rmdir()
    except OSError:
        pass

    print(f"\n[完成] 总行数: {total_rows:,} -> {pq_path}")
    return pq_path


# ============================================================
#  动态数据读取接口
# ============================================================

def get_ais_dynamic(
    year: int = 25,
    columns: list[str] = None,
    date_start: str = None,
    date_end: str = None,
    mmsi_list: list[int] = None,
    bbox: tuple = None,
    limit: int = 100_000,
) -> gpd.GeoDataFrame:
    """
    读取 AIS 动态数据，支持按年份和条件过滤。
    year: 25=2025年, 26=2026年
    """
    pq_path = build_ais_parquet(year)

    user_columns = columns or [
        "mmsi", "acqtime", "target_type", "data_supplier", "data_source",
        "move_status", "longitude", "latitude", "area_id", "speed_knots",
        "speed_ms", "cog_deg", "heading_deg", "date"
    ]

    read_columns = set(user_columns)
    if date_start or date_end:
        read_columns.add("date")
    if mmsi_list:
        read_columns.add("mmsi")
    if bbox:
        read_columns.update(["longitude", "latitude"])
    read_columns.update(["longitude", "latitude"])
    read_columns = list(read_columns)

    pf = pq.ParquetFile(pq_path)
    
    batches = []
    total_rows = 0
    batch_size = 100_000

    for batch in pf.iter_batches(batch_size=batch_size, columns=read_columns):
        df = batch.to_pandas()

        mask = pd.Series(True, index=df.index)
        if date_start:
            mask &= df["date"] >= pd.Timestamp(date_start)
        if date_end:
            mask &= df["date"] <= pd.Timestamp(date_end)
        if mmsi_list:
            mask &= df["mmsi"].isin(mmsi_list)
        if bbox:
            min_lon, min_lat, max_lon, max_lat = bbox
            mask &= (df["longitude"] >= min_lon) & (df["longitude"] <= max_lon)
            mask &= (df["latitude"] >= min_lat) & (df["latitude"] <= max_lat)

        filtered = df[mask]
        if len(filtered) > 0:
            keep_cols = [c for c in user_columns if c in filtered.columns]
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
    year: int = 25,
    columns: list[str] = None,
    date_start: str = None,
    date_end: str = None,
    mmsi_list: list[int] = None,
    bbox: tuple = None,
    batch_size: int = 100_000,
):
    """
    迭代器版：逐批返回 GeoDataFrame。
    year: 25=2025年, 26=2026年
    """
    pq_path = build_ais_parquet(year)

    user_columns = columns or [
        "mmsi", "acqtime", "target_type", "data_supplier", "data_source",
        "move_status", "longitude", "latitude", "area_id", "speed_knots",
        "speed_ms", "cog_deg", "heading_deg", "date"
    ]

    read_columns = set(user_columns)
    if date_start or date_end:
        read_columns.add("date")
    if mmsi_list:
        read_columns.add("mmsi")
    if bbox:
        read_columns.update(["longitude", "latitude"])
    read_columns.update(["longitude", "latitude"])
    read_columns = list(read_columns)

    pf = pq.ParquetFile(pq_path)

    for batch in pf.iter_batches(batch_size=batch_size, columns=read_columns):
        df = batch.to_pandas()

        mask = pd.Series(True, index=df.index)
        if date_start:
            mask &= df["date"] >= pd.Timestamp(date_start)
        if date_end:
            mask &= df["date"] <= pd.Timestamp(date_end)
        if mmsi_list:
            mask &= df["mmsi"].isin(mmsi_list)
        if bbox:
            min_lon, min_lat, max_lon, max_lat = bbox
            mask &= (df["longitude"] >= min_lon) & (df["longitude"] <= max_lon)
            mask &= (df["latitude"] >= min_lat) & (df["latitude"] <= max_lat)

        filtered = df[mask]
        if len(filtered) == 0:
            del df, batch
            continue

        keep_cols = [c for c in user_columns if c in filtered.columns]
        filtered = filtered[keep_cols]

        gdf = gpd.GeoDataFrame(
            filtered,
            geometry=gpd.points_from_xy(filtered.longitude, filtered.latitude),
            crs="EPSG:4326"
        )
        yield gdf

        del df, batch, gdf


# ============================================================
#  静态数据包装类（支持按 MMSI 查询，不加载全量）
# ============================================================

class StaticData:
    """静态数据包装类，支持按 MMSI 查询和迭代，不加载全量数据"""
    
    def __init__(self, pq_path: Path):
        self.pq_path = pq_path
        self._pf = pq.ParquetFile(pq_path)
        self.columns = self._pf.schema.names
    
    def get_by_mmsi(self, mmsi: int) -> pd.Series | None:
        """按 MMSI 查询单条记录，逐批扫描"""
        for batch in self._pf.iter_batches(batch_size=100000):
            df = batch.to_pandas()
            mask = df["mmsi"] == mmsi
            if mask.any():
                return df[mask].iloc[0]
            del df, batch
        return None
    
    def get_by_mmsi_list(self, mmsi_list: list[int]) -> pd.DataFrame:
        """按 MMSI 列表批量查询，逐批过滤避免内存问题"""
        batches = []
        mmsi_set = set(mmsi_list)
        for batch in self._pf.iter_batches(batch_size=100000):
            df = batch.to_pandas()
            filtered = df[df["mmsi"].isin(mmsi_set)]
            if len(filtered) > 0:
                batches.append(filtered)
            del df, batch
        if not batches:
            return pd.DataFrame(columns=self.columns)
        return pd.concat(batches, ignore_index=True)
    
    def iter_batches(self, batch_size: int = 100000):
        """逐批迭代"""
        for batch in self._pf.iter_batches(batch_size=batch_size):
            yield batch.to_pandas()
    
    def head(self, n: int = 5) -> pd.DataFrame:
        """查看前 n 行"""
        for batch in self._pf.iter_batches(batch_size=n):
            return batch.to_pandas().head(n)
        return pd.DataFrame(columns=self.columns)
    
    def __len__(self):
        return self._pf.metadata.num_rows
    
    def __repr__(self):
        return f"StaticData({self.pq_path.name}, {len(self):,} rows, {len(self.columns)} cols)"


@lru_cache(maxsize=1)
def get_ais_static() -> StaticData:
    """读取 AIS 静态数据，已做清洗"""

    pq_path = CACHE / "ais_static.parquet"

    if pq_path.exists():
        return StaticData(pq_path)
    if not STATIC_DIR.exists():
        raise FileNotFoundError(f"静态数据目录不存在: {STATIC_DIR}")

    def normalize_column_name(col: str) -> str:
        return col.strip().lower().replace(" ", "_")

    STATIC_COLUMN_MAP = {
        "shipname": "ship_name",
        "shiptype": "ship_type",
        "breadth": "width",
    }

    STATIC_SCHEMA = {
        "mmsi": "int64",
        "imo": "str",
        "callsign": "str",
        "ship_name": "str",
        "ship_type": "Int64",
        "length": "float64",
        "width": "float64",
        "pos_fixing_device": "str",
        "eta": "str",
        "draught": "float64",
        "destination": "str",
        "classtype": "str",
        "receivetime": "datetime64[ns, UTC]",
        "to_bow": "Int64",
        "to_stern": "Int64",
        "to_port": "Int64",
        "to_starboard": "Int64",
        "month": "str",
    }

    rows = []
    for csv in sorted(STATIC_DIR.glob("*.csv")):
        month = csv.stem.split("_")[-1]
        try:
            df = pd.read_csv(csv, low_memory=False)
            for drop_col in ["Unnamed: 0", "unnamed: 0", "unnamed:_0"]:
                if drop_col in df.columns:
                    df = df.drop(columns=[drop_col])
                    print(f"    已删除索引列: {drop_col}")
            df.columns = [normalize_column_name(c) for c in df.columns]
            df = df.rename(columns=STATIC_COLUMN_MAP)
            df = df.assign(month=month)
            rows.append(df)
            print(f"  [静态] {csv.name} | {len(df):,} 行 | month={month}")
            print(f"    列名: {list(df.columns)}")
        except Exception as e:
            print(f"  [错误] {csv.name}: {e}")
            raise

    if not rows:
        raise FileNotFoundError(f"在 {STATIC_DIR} 中未找到静态数据")
    df = pd.concat(rows, ignore_index=True)

    print(f"  清洗 MMSI...")
    before = len(df)
    df["mmsi"] = (
        df["mmsi"]
        .astype(str)
        .str.strip()
        .str.strip('"')
        .str.strip("'")
    )
    mask = df["mmsi"].str.match(r"^\d{9}$")
    invalid = (~mask).sum()
    df = df[mask].copy()
    df["mmsi"] = df["mmsi"].astype("int64")
    print(f"    过滤无效 MMSI: {invalid:,} 条去除，保留 {len(df):,} 条")

    def clean_str(series: pd.Series) -> pd.Series:
        s = series.astype(str).str.strip().str.strip('"').str.strip("'")
        s = s.replace(r"^\s*$", pd.NA, regex=True)
        s = s.replace(["nan", "None", "NULL", "null", "NaN", "NA"], pd.NA)
        return s

    def clean_int(series: pd.Series) -> pd.Series:
        s = clean_str(series)
        return pd.to_numeric(s, errors="coerce").astype("Int64")

    def clean_float(series: pd.Series) -> pd.Series:
        s = clean_str(series)
        return pd.to_numeric(s, errors="coerce").astype("float64")

    print(f"  按字段说明表统一转换类型...")
    for col, dtype in STATIC_SCHEMA.items():
        if col not in df.columns:
            continue
        if col == "mmsi":
            continue
        if col == "receivetime":
            continue
        try:
            if dtype == "str":
                df[col] = clean_str(df[col])
            elif dtype == "Int64":
                df[col] = clean_int(df[col])
            elif dtype == "int64":
                df[col] = clean_int(df[col]).astype("int64")
            elif dtype == "float64":
                df[col] = clean_float(df[col])
            elif dtype.startswith("datetime"):
                df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)
        except Exception as e:
            print(f"    警告: 列 {col} 转换失败({e})，降级为字符串")
            df[col] = clean_str(df[col])

    for col in df.columns:
        if col not in STATIC_SCHEMA:
            df[col] = clean_str(df[col])

    if "receivetime" in df.columns:
        print(f"  处理 receivetime...")
        before_invalid = df["receivetime"].isna().sum()

        def parse_receivetime(val):
            if pd.isna(val):
                return pd.NaT
            s = str(val).strip().strip('"').strip("'")
            if s.lower() in ("", "nan", "none", "null"):
                return pd.NaT
            try:
                clean = s.replace(".", "", 1).replace("-", "", 1)
                if clean.isdigit():
                    ts = float(s)
                    unit = "ms" if ts > 1e12 else "s"
                    return pd.to_datetime(ts, unit=unit, utc=True)
            except:
                pass
            try:
                return pd.to_datetime(s, utc=True)
            except:
                return pd.NaT

        df["receivetime"] = df["receivetime"].apply(parse_receivetime)
        after_invalid = df["receivetime"].isna().sum()
        if after_invalid > before_invalid:
            print(f"    警告: {after_invalid - before_invalid} 条 receivetime 解析失败转为 NaT")

    print(f"  类型转换完成")
    print(f"\n[去重] 合并前: {len(df):,} 行")
    df["month"] = df["month"].astype(str)

    def parse_eta(eta_str):
        if pd.isna(eta_str) or str(eta_str).strip() == "":
            return "00-00 00:00"
        try:
            parts = str(eta_str).strip().split()
            if len(parts) == 2:
                mm_dd = parts[0].split("-")
                hh_mm = parts[1].split(":")
                if len(mm_dd) == 2 and len(hh_mm) == 2:
                    return f"{int(mm_dd[0]):02d}-{int(mm_dd[1]):02d} {int(hh_mm[0]):02d}:{int(hh_mm[1]):02d}"
        except:
            pass
        return str(eta_str)

    if "eta" in df.columns:
        df["_eta_sort"] = df["eta"].apply(parse_eta)
        df = df.sort_values(["mmsi", "month", "_eta_sort"], ascending=[True, False, False])
        df = df.drop(columns=["_eta_sort"])
    else:
        df = df.sort_values(["mmsi", "month"], ascending=[True, False])

    df = df.drop_duplicates(subset=["mmsi"], keep="first")

    after = len(df)
    print(f"  按 MMSI 去重: {before:,} -> {after:,} 行（去除 {before - after:,} 条重复）")
    print(f"  MMSI 唯一值: {df['mmsi'].nunique():,}")

    df.to_parquet(pq_path, compression="zstd")
    print(f"[静态数据缓存] {pq_path} | {len(df):,} 行")
    return StaticData(pq_path)


# ============================================================
#  船舶档案
# ============================================================

@lru_cache(maxsize=1)
def get_ship_archive() -> pd.DataFrame:
    pq_path = CACHE / "ship_archive.parquet"
    if pq_path.exists():
        return pd.read_parquet(pq_path)

    if not ARCHIVE_DIR.exists():
        raise FileNotFoundError(f"档案目录不存在: {ARCHIVE_DIR}")

    rows = []
    for csv in sorted(ARCHIVE_DIR.glob("*.csv")):
        ship_type = csv.stem.split("_")[0]
        try:
            df = pd.read_csv(csv, low_memory=False)
            df = df.assign(archive_type=ship_type)
            rows.append(df)
            print(f"  [档案] {csv.name} | {len(df):,} 行")
        except Exception as e:
            print(f"  [错误] {csv.name}: {e}")
            raise

    if not rows:
        raise FileNotFoundError(f"在 {ARCHIVE_DIR} 中未找到档案数据")

    df = pd.concat(rows, ignore_index=True)
    df.to_parquet(pq_path)
    print(f"[档案缓存] {pq_path} | {len(df):,} 行")
    return df


# ============================================================
#  主程序
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("AIS 数据加载测试")
    print(f"缓存目录: {CACHE}")
    print("=" * 60)

    print("\n>>> 动态数据（1天 + limit=1万）...")
    dynamic = get_ais_dynamic(
        date_start="2025-03-01",
        date_end="2025-03-01",
        limit=10000,
        columns=["mmsi", "acqtime", "longitude", "latitude", "speed_knots"]
    )
    print(f"动态数据: {len(dynamic):,} 行")
    print(dynamic.head(3))

    print("\n>>> 动态数据（2026）...")
    dynamic = get_ais_dynamic(
        year=26,
        date_start="2026-03-01",
        limit=10000
    )
    print(f"动态数据: {len(dynamic):,} 行")
    print(dynamic.head(3))

    print("\n>>> 静态数据...")
    static = get_ais_static()
    print(f"静态数据: {static}")
    print("前3行:")
    print(static.head(3))

    print("\n>>> 按 MMSI 查询示例...")
    record = static.get_by_mmsi(412549105)
    if record is not None:
        print(f"找到 MMSI 412549105: {record['ship_name']}")
    else:
        print("未找到")

    print("\n>>> 船舶档案...")
    archive = get_ship_archive()
    print(f"档案数据: {len(archive):,} 行")
    print(archive.head(3))

    print("\n" + "=" * 60)
    print("全部完成")
    