import os
import pyarrow as pa
import pyarrow.parquet as pq
from datalib import get_ais_dynamic_iter

regions = {
    "Strait_of_Hormuz": {"lon": (54.0, 59.0), "lat": (23.0, 28.0), "desc": "霍尔木兹海峡"},
    "Strait_of_Malacca": {"lon": (100.0, 105.0), "lat": (-1.0, 4.0), "desc": "马六甲海峡"},
    "Cape_of_Good_Hope": {"lon": (17.0, 27.0), "lat": (-40.5, -30.5), "desc": "好望角"},
    "Suez_Canal": {"lon": (30.0, 35.0), "lat": (28.0, 33.0), "desc": "苏伊士运河"},
}

output_dir = "../database/ais_dynamic_by_region"
os.makedirs(output_dir, exist_ok=True)

for year in [25, 26]:
    for region_name, region in regions.items():

        out_path = os.path.join(output_dir, f"ais_{region_name}_20{year}.parquet")

        bbox = (region["lon"][0], region["lat"][0], region["lon"][1], region["lat"][1])

        iter_gdf = get_ais_dynamic_iter(
            year=year,
            bbox=bbox,
            columns=["mmsi", "longitude", "latitude", "speed_knots"],
            batch_size=100_000,
        )

        writer = None
        total = 0

        for gdf in iter_gdf:
            if "geometry" in gdf.columns:
                gdf = gdf.drop(columns=["geometry"])

            table = pa.Table.from_pandas(gdf, preserve_index=False)

            if writer is None:
                writer = pq.ParquetWriter(out_path, table.schema, compression="zstd")

            writer.write_table(table)
            total += len(gdf)
            print(f"{region_name} 20{year}: +{len(gdf):,} = {total:,} 行")
            del gdf, table

        if writer:
            writer.close()
            print(f"  ✓ 完成: {total:,} 行 -> {out_path}")
        else:
            import pandas as pd

            pd.DataFrame(columns=["mmsi", "longitude", "latitude", "speed_knots"]).to_parquet(out_path)
            print(f"  ⚠ 无数据")

print("\\n全部完成！")
