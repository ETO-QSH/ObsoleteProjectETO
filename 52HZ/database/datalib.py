import pandas as pd
import pyarrow as pa
import geopandas as gpd
import pyarrow.parquet as pq

from pathlib import Path
from functools import lru_cache


ROOT = Path(__file__).parent
RAW = ROOT / "data_raw"
CACHE = ROOT / "data_cache"
CACHE.mkdir(exist_ok=True)


# ---------- 集装箱船 AIS 数据 ----------
@lru_cache(maxsize=1)
def get_ais() -> gpd.GeoDataFrame:
    pq = CACHE / "ais.parquet"
    if pq.exists():
        return gpd.read_parquet(pq)

    rows = []
    for csv in RAW.glob("aisdb/**/*.csv"):
        date = pd.to_datetime(csv.stem, format="%Y%m%d")
        month = csv.parent.name

        df = (
            pd.read_csv(csv)
            .assign(
                date=date,
                month=month
            )
        )
        rows.append(df)

    if not rows:
        raise FileNotFoundError("Not found ais file")

    df = pd.concat(rows, ignore_index=True)
    df["acqtime"] = pd.to_datetime(df["acqtime"], utc=True)

    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df.longitude, df.latitude),
        crs="EPSG:4326"
    )
    gdf.to_parquet(pq)
    return gdf


# ---------- 三张 Excel 表 ----------
@lru_cache(maxsize=1)
def get_excel() -> dict[str, pd.DataFrame]:
    file_map = {
        "ship_type":   "分航线船型分布.xls",
        "line_speed": "分航线平均航行速度(月）.xls",
        "reliability": "全球主干航线到离港或收发货准班率指数.xls",
    }

    excel_dir = CACHE / "excel"
    excel_dir.mkdir(exist_ok=True)

    for key, name in file_map.items():
        pq_path = excel_dir / f"{key}.parquet"
        if not pq_path.exists():
            xls_path = RAW / name
            if not xls_path.exists():
                raise FileNotFoundError(f"Not found {name}.xls file")
            data = pd.read_excel(xls_path, sheet_name=0)
            pq.write_table(pa.Table.from_pandas(data), pq_path)

    return {key: pd.read_parquet(excel_dir / f"{key}.parquet") for key in file_map}


# ---------- 集装箱船信息 ----------
@lru_cache(maxsize=1)
def get_ships() -> pd.DataFrame:
    pq = CACHE / "ships.parquet"
    if pq.exists():
        return pd.read_parquet(pq)

    csv = RAW / "集装箱船信息.csv"
    if not csv.exists():
        raise FileNotFoundError("Not found 集装箱船信息.csv file")

    df = (
        pd.read_csv(csv)
        .set_index("ship_id")
        .sort_index()
    )

    df.to_parquet(pq)
    return df


if __name__ == '__main__':
    ais = get_ais()
    ships = get_ships()
    excel = get_excel()
