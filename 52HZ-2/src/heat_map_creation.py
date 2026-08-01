import math
import numpy as np
import pandas as pd
from pathlib import Path
import cartopy.crs as crs
import matplotlib.pyplot as plt
import cartopy.feature as feature
from datalib import get_ais_static
import matplotlib.colors as mcolors
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

INPUT_DIR = Path("../database/ais_dynamic_ocean_only")
OUT_PUT = Path("../output/heat_map")
OUT_PUT.mkdir(exist_ok=True)

DPI = 100
CELL_M = 1000
W, H = 640, 720
HEATMAP_SIZE = 480

plt.rcParams['font.sans-serif'] = ['Lolita']
CRS_MAP = crs.PlateCarree()
earth_radius = 6378137
years = [25, 26]

regions = {
    "Strait_of_Hormuz": {"lon": (54.0, 59.0), "lat": (23.0, 28.0), "desc": "霍尔木兹海峡"},
    "Strait_of_Malacca": {"lon": (100.0, 105.0), "lat": (-1.0, 4.0), "desc": "马六甲海峡"},
    "Cape_of_Good_Hope": {"lon": (17.0, 27.0), "lat": (-40.5, -30.5), "desc": "好望角"},
    "Suez_Canal": {"lon": (30.0, 35.0), "lat": (28.0, 33.0), "desc": "苏伊士运河"},
}

cmap_rho = plt.cm.YlOrRd
cmap_speed = plt.cm.YlGn

static_data = get_ais_static()
print(f"[静态数据] {static_data}")

TANKER_TYPES = {80, 81, 82, 83, 84, 85, 88, 89}
LNG_TYPES = {86}

K_TANKER = 0.70
K_LNG = 0.46

cmap_tanker = plt.cm.Oranges
cmap_lng = plt.cm.Blues


def compute_cell_size(lat_min, lat_max):
    ref_lat = (lat_min + lat_max) / 2
    cell_lon_deg = CELL_M / (math.cos(math.radians(ref_lat)) * 2 * math.pi * earth_radius / 360)
    cell_lat_deg = CELL_M / (2 * math.pi * earth_radius / 360)
    return cell_lon_deg, cell_lat_deg


def scale_mark_ticks(lon_min, lon_max, lat_min, lat_max):
    lon_start = np.round(lon_min, 1)
    lon_end = np.round(lon_max, 1)
    lat_start = np.round(lat_min, 1)
    lat_end = np.round(lat_max, 1)

    xstep = (lon_max - lon_min) / 5
    ystep = (lat_max - lat_min) / 5
    xstart = xstep / 2
    ystart = ystep / 2

    xticks = np.round(np.arange(lon_start + xstart, lon_end, xstep), 1)
    yticks = np.round(np.arange(lat_start + ystart, lat_end, ystep), 1)
    return xticks, yticks


def load_ais_data(region_name, year):
    path = INPUT_DIR / f"ais_{region_name}_20{year}_ocean.parquet"
    if not path.exists():
        print(f"⚠ 文件不存在: {path}")
        return None
    df = pd.read_parquet(path)
    print(f"  加载 {path.name}: {len(df):,} 行")
    return df


def rasterize(df, lon_min, lat_min, cell_lon_deg, cell_lat_deg):
    if df is None or len(df) == 0:
        return pd.Series(dtype=float), pd.Series(dtype=float)

    df = df.copy()
    df['gx'] = ((df['longitude'] - lon_min) / cell_lon_deg).astype(int)
    df['gy'] = ((df['latitude'] - lat_min) / cell_lat_deg).astype(int)

    rho = df.groupby(['gx', 'gy'])['mmsi'].nunique()

    speed_col = 'speed_knots' if 'speed_knots' in df.columns else 'speed'
    speed = df.groupby(['gx', 'gy'])[speed_col].mean()

    return rho, speed


def rasterize_capacity(df, lon_min, lat_min, cell_lon_deg, cell_lat_deg, static_data):
    if df is None or len(df) == 0:
        return {'Tanker': pd.Series(dtype=float), 'LNG': pd.Series(dtype=float)}
    df = df.copy()

    mmsi_list = df['mmsi'].unique().tolist()
    print(f"    查询静态数据: {len(mmsi_list):,} 个唯一 MMSI")
    static_df = static_data.get_by_mmsi_list(mmsi_list)
    print(f"    静态数据返回: {len(static_df):,} 条记录")

    if len(static_df) == 0:
        return {'Tanker': pd.Series(dtype=float), 'LNG': pd.Series(dtype=float)}

    static_df = static_df.copy()
    static_df['vessel_type'] = static_df['ship_type'].apply(
        lambda x: 'Tanker' if x in TANKER_TYPES else ('LNG' if x in LNG_TYPES else None)
    )
    static_df = static_df[static_df['vessel_type'].notna()]

    static_df['draught_m'] = static_df['draught'] / 1000.0
    static_df['ship_dead'] = static_df.apply(
        lambda row: (
            K_TANKER * row['length'] * row['width'] * row['draught_m']
            if row['vessel_type'] == 'Tanker'
            else K_LNG * row['length'] * row['width'] * row['draught_m']
        ),
        axis=1
    )

    static_df = static_df.sort_values('receivetime').drop_duplicates('mmsi', keep='last')
    lookup = static_df.set_index('mmsi')[['vessel_type', 'ship_dead']]
    df = df.join(lookup, on='mmsi', how='inner')

    if len(df) == 0:
        return {'Tanker': pd.Series(dtype=float), 'LNG': pd.Series(dtype=float)}

    df['gx'] = ((df['longitude'] - lon_min) / cell_lon_deg).astype(int)
    df['gy'] = ((df['latitude'] - lat_min) / cell_lat_deg).astype(int)

    result = {}
    for ship_type in ['Tanker', 'LNG']:
        subset = df[df['vessel_type'] == ship_type]
        if len(subset) == 0:
            result[ship_type] = pd.Series(dtype=float)
        else:
            result[ship_type] = subset.groupby(['gx', 'gy'])['ship_dead'].sum()
    return result


def compute_grid_extent(lon_min, lon_max, lat_min, lat_max, cell_lon_deg, cell_lat_deg):
    nx = 1 + int((lon_max - lon_min) / cell_lon_deg)
    ny = 1 + int((lat_max - lat_min) / cell_lat_deg)
    lons = np.linspace(lon_min, lon_max, nx)
    lats = np.linspace(lat_min, lat_max, ny)
    return nx, ny, lons, lats


def fill_grid(rho_or_speed, nx, ny):
    grid = np.full((ny - 1, nx - 1), np.nan)
    if len(rho_or_speed) == 0:
        return grid
    for (gx, gy), val in rho_or_speed.items():
        if 0 <= gy < ny - 1 and 0 <= gx < nx - 1:
            grid[gy, gx] = val
    return grid


def draw_heatmap(grid, lons, lats, region, title, cmap, norm, out_path):
    fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI)

    left = (W - HEATMAP_SIZE) / 2 / W
    bottom = 0.1
    width = HEATMAP_SIZE / W
    height = HEATMAP_SIZE / H

    lon_min, lon_max, lat_min, lat_max = region
    ax = fig.add_axes((left, bottom, width, height), projection=CRS_MAP)
    ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=CRS_MAP)

    ax.add_feature(feature.LAND.with_scale('10m'), facecolor='lightgray')
    ax.add_feature(feature.COASTLINE.with_scale('10m'))
    ax.add_feature(feature.BORDERS.with_scale('10m'), linestyle=':')

    ax.pcolormesh(
        lons, lats, grid,
        cmap=cmap,
        norm=norm,
        transform=CRS_MAP,
        shading='auto'
    )

    xticks, yticks = scale_mark_ticks(lon_min, lon_max, lat_min, lat_max)

    ax.set_xticks(xticks, crs=CRS_MAP)
    ax.set_yticks(yticks, crs=CRS_MAP)

    ax.xaxis.set_major_formatter(LongitudeFormatter(number_format='.1f'))
    ax.yaxis.set_major_formatter(LatitudeFormatter(number_format='.1f'))

    ax.tick_params(axis='both', labelsize=10, direction='out', length=5, width=1)
    ax.tick_params(axis='x', which='both', top=True, bottom=True, labeltop=True, labelbottom=True)
    ax.tick_params(axis='y', which='both', left=True, right=True, labelleft=True, labelright=True)

    fig.text(0.5, 0.9, title, ha='center', va='center', fontsize=16, fontweight='bold')

    fig.savefig(out_path, dpi=DPI, bbox_inches='tight')
    plt.close(fig)
    print(f"  ✅ 已保存: {out_path}")


print("=" * 60)
print("AIS 热力图绘制")
print("=" * 60)

for region_name, cfg in regions.items():
    print(f"\n{'=' * 60}")
    print(f"🗺 区域: {cfg['desc']} ({region_name})")
    print(f"{'=' * 60}")

    lon_min, lon_max = cfg["lon"]
    lat_min, lat_max = cfg["lat"]

    cell_lon_deg, cell_lat_deg = compute_cell_size(lat_min, lat_max)
    nx, ny, lons, lats = compute_grid_extent(lon_min, lon_max, lat_min, lat_max, cell_lon_deg, cell_lat_deg)

    print(f"  网格: nx={nx}, ny={ny}, cell={cell_lon_deg:.5f}°×{cell_lat_deg:.5f}°")

    all_rho = {}
    all_speed = {}

    for year in years:
        df = load_ais_data(region_name, year)
        rho, speed = rasterize(df, lon_min, lat_min, cell_lon_deg, cell_lat_deg)
        all_rho[year] = rho
        all_speed[year] = speed
        print(f"  20{year}年: 密度栅格 {len(rho)} 个, 速度栅格 {len(speed)} 个")

    rho_max_25 = all_rho[25].max() if len(all_rho[25]) > 0 else 1
    rho_max_26 = all_rho[26].max() if len(all_rho[26]) > 0 else 1
    rho_vmax = max(rho_max_25, rho_max_26)
    if pd.isna(rho_vmax) or rho_vmax <= 0:
        rho_vmax = 1

    speed_max_25 = all_speed[25].max() if len(all_speed[25]) > 0 else 1
    speed_max_26 = all_speed[26].max() if len(all_speed[26]) > 0 else 1
    speed_vmax = max(speed_max_25, speed_max_26)
    if pd.isna(speed_vmax) or speed_vmax <= 0:
        speed_vmax = 1

    print(f"  密度上限: {rho_vmax:.1f}, 速度上限: {speed_vmax:.1f}")

    rho_norm = mcolors.PowerNorm(vmin=0, vmax=rho_vmax, gamma=0.33)
    speed_norm = mcolors.PowerNorm(vmin=0, vmax=speed_vmax, gamma=0.5)

    all_tanker = {}
    all_lng = {}

    for year in years:
        df = load_ais_data(region_name, year)
        cap = rasterize_capacity(df, lon_min, lat_min, cell_lon_deg, cell_lat_deg, static_data)
        all_tanker[year] = cap['Tanker']
        all_lng[year] = cap['LNG']
        print(f"  20{year}年: Tanker {len(cap['Tanker'])}格, LNG {len(cap['LNG'])}格")

    tanker_max_25 = all_tanker[25].max() if len(all_tanker[25]) > 0 else 1
    tanker_max_26 = all_tanker[26].max() if len(all_tanker[26]) > 0 else 1
    tanker_vmax = max(tanker_max_25, tanker_max_26)
    if pd.isna(tanker_vmax) or tanker_vmax <= 0:
        tanker_vmax = 1

    lng_max_25 = all_lng[25].max() if len(all_lng[25]) > 0 else 1
    lng_max_26 = all_lng[26].max() if len(all_lng[26]) > 0 else 1
    lng_vmax = max(lng_max_25, lng_max_26)
    if pd.isna(lng_vmax) or lng_vmax <= 0:
        lng_vmax = 1

    print(f"  Tanker运力上限: {tanker_vmax:,.0f}, LNG运力上限: {lng_vmax:,.0f}")

    tanker_norm = mcolors.PowerNorm(vmin=0, vmax=tanker_vmax, gamma=0.25)
    lng_norm = mcolors.PowerNorm(vmin=0, vmax=lng_vmax, gamma=0.2)

    for year in years:
        grid_rho = fill_grid(all_rho[year], nx, ny)
        out_rho = OUT_PUT / f"{region_name}_20{year}_rho_{W}x{H}.png"
        region = lon_min, lon_max, lat_min, lat_max
        draw_heatmap(
            grid_rho, lons, lats, region,
            title=f"{cfg['desc']} 20{year}年 船舶密度热力图",
            cmap=cmap_rho,
            norm=rho_norm,
            out_path=out_rho,
        )

        grid_speed = fill_grid(all_speed[year], nx, ny)
        out_speed = OUT_PUT / f"{region_name}_20{year}_speed_{W}x{H}.png"
        draw_heatmap(
            grid_speed, lons, lats, region,
            title=f"{cfg['desc']} 20{year}年 平均航速热力图",
            cmap=cmap_speed,
            norm=speed_norm,
            out_path=out_speed,
        )

        grid_tanker = fill_grid(all_tanker[year], nx, ny)
        out_tanker = OUT_PUT / f"{region_name}_20{year}_tanker_{W}x{H}.png"
        draw_heatmap(
            grid_tanker, lons, lats, region,
            title=f"{cfg['desc']} 20{year}年 石油运力热力图",
            cmap=cmap_tanker,
            norm=tanker_norm,
            out_path=out_tanker,
        )

        grid_lng = fill_grid(all_lng[year], nx, ny)
        out_lng = OUT_PUT / f"{region_name}_20{year}_lng_{W}x{H}.png"
        draw_heatmap(
            grid_lng, lons, lats, region,
            title=f"{cfg['desc']} 20{year}年 天然气运力热力图",
            cmap=cmap_lng,
            norm=lng_norm,
            out_path=out_lng,
        )

print(f"\n{'=' * 60}")
print("✅ 全部完成！")
print(f"输出目录: {OUT_PUT}")
print(f"共生成 {len(regions) * len(years) * 2} 张图")
