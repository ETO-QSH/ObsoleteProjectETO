import os
import geopandas as gpd
from shapely.geometry import box


INPUT_SHP = "./World_EEZ_v12_20231025/eez_v12.shp"
OUTPUT_DIR = "./corridor"
os.makedirs(OUTPUT_DIR, exist_ok=True)

eez = gpd.read_file(INPUT_SHP)
print(f"坐标系: {eez.crs}")

regions = {
    "Strait_of_Hormuz": {
        "lon": (54.0, 59.0),
        "lat": (23.0, 28.0),
        "desc": "霍尔木兹海峡"
    },
    "Strait_of_Malacca": {
        "lon": (100.0, 105.0),
        "lat": (-1.0, 4.0),
        "desc": "马六甲海峡"
    },
    "Cape_of_Good_Hope": {
        "lon": (17.0, 27.0),
        "lat": (-40.5, -30.5),
        "desc": "好望角"
    },
    "Suez_Canal": {
        "lon": (30.0, 35.0),
        "lat": (28.0, 33.0),
        "desc": "苏伊士运河"
    }
}

for name, cfg in regions.items():
    print(f"\n正在裁剪: {cfg['desc']} ({name})...")
    candidates = eez.cx[cfg["lon"][0]:cfg["lon"][1], cfg["lat"][0]:cfg["lat"][1]]
    bbox = box(cfg["lon"][0], cfg["lat"][0], cfg["lon"][1], cfg["lat"][1])
    bbox_gdf = gpd.GeoDataFrame(geometry=[bbox], crs=eez.crs)

    clipped = gpd.clip(candidates, bbox_gdf)
    output_path = os.path.join(OUTPUT_DIR, f"{name}.geojson")
    clipped.to_file(output_path, driver="GeoJSON")
    print(f"  - 已保存: {output_path}")

print("\n✅ 全部完成！4 个矩形裁剪 GeoJSON 已生成:")
for f in sorted(os.listdir(OUTPUT_DIR)):
    if f.endswith(".geojson"):
        print(f"   {OUTPUT_DIR}/{f}")
