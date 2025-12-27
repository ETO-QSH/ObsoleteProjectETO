import geopandas as gpd
import numpy as np
import pandas as pd

from database.datalib import get_ais
from config import CORRIDOR_GEOJSON


def corridor_filter() -> gpd.GeoDataFrame:
    ais = get_ais()

    # 它喵的我这一行代码浪费我一个小时
    ais['acqtime'] = ais['acqtime'].astype(np.int64)

    # 读取并裁剪走廊多边形
    corr = gpd.read_file(CORRIDOR_GEOJSON).to_crs('EPSG:4326')
    gdf = gpd.sjoin(ais.to_crs('EPSG:4326'), corr, predicate='within')

    # 转换 Unix 时间戳为 datetime，并转换时区
    gdf['hour'] = pd.to_datetime(gdf['acqtime'], unit='s', utc=True).dt.tz_convert('Asia/Shanghai')

    # 2 小时区间字符串
    gdf['interval'] = gdf['hour'].dt.hour.apply(lambda h: f"{(h//2)*2}-{(h//2)*2+2}")

    return gdf
