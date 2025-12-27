import pandas as pd
import geopandas as gpd
from pathlib import Path


data_raw = Path(r"D:\Desktop\Desktop\52HZ\4、MR型成品油轮、阿芙拉型成品油轮、VLCC油轮，2020年-2024年，每年1-3月的船舶轨迹数据")
CACHE = data_raw / "data_cache"
CACHE.mkdir(exist_ok=True)


def process_csv(file_path: Path) -> None:
    df = pd.read_csv(file_path)[["latitude", "longitude"]]
    pq_file = CACHE / f"{file_path.stem}.parquet"
    df.to_parquet(pq_file)


def get_ais(dir_zh: str, year: str) -> gpd.GeoDataFrame:
    names = {"MR型成品油轮": "MR", "VLCC油轮": "VLCC", "阿芙拉型成品油轮": "AFRAMAX"}
    file_name = f"{names[dir_zh]}_{year}.csv"
    csv_file = data_raw / dir_zh / file_name
    pq_file = CACHE / f"{names[dir_zh]}_{year}.parquet"

    if pq_file.exists():
        df = pd.read_parquet(pq_file)
    elif csv_file.exists():
        df = pd.read_csv(csv_file)[["longitude", "latitude"]].dropna()
        gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude),crs="EPSG:3857")
        gdf.to_crs("EPSG:4326").to_parquet(pq_file, index=False)
    else:
        raise FileNotFoundError(f"File '{file_name}' not found for '{dir_zh}'")

    return gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs="EPSG:4326")


if __name__ == '__main__':
    for dir in ["MR型成品油轮", "VLCC油轮", "阿芙拉型成品油轮"]:
        for year in ["2020", "2021", "2022", "2023", "2024"]:
            ais_data = get_ais(dir, year)
