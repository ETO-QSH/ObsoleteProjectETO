import os
import gc
import pyarrow as pa
import geopandas as gpd
import pyarrow.parquet as pq

CORRIDOR_DIR = "../external/WORLDEEZ/corridor"
INPUT_DIR = "../database/ais_dynamic_by_region"
OUTPUT_DIR = "../database/ais_dynamic_ocean_only"
os.makedirs(OUTPUT_DIR, exist_ok=True)

regions = [
    "Strait_of_Hormuz",
    "Strait_of_Malacca",
    "Cape_of_Good_Hope",
    "Suez_Canal",
]

years = [25, 26]
BATCH_SIZE = 100_000


def load_ocean_polygon(region_name):
    geojson_path = os.path.join(CORRIDOR_DIR, f"{region_name}.geojson")

    if not os.path.exists(geojson_path):
        raise FileNotFoundError(f"找不到海洋 GeoJSON: {geojson_path}")

    gdf = gpd.read_file(geojson_path)

    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")
    elif gdf.crs.to_string() != "EPSG:4326":
        gdf = gdf.to_crs("EPSG:4326")

    print(f"  加载 {region_name}.geojson: {len(gdf)} 个多边形, CRS={gdf.crs}")
    return gdf


def filter_ocean_points_sjoin(df, ocean_gdf):
    if len(df) == 0:
        return df

    points_gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df.longitude, df.latitude),
        crs="EPSG:4326"
    )

    joined = gpd.sjoin(
        points_gdf,
        ocean_gdf[["geometry"]],
        predicate="within",
        how="inner"
    )

    result = joined.drop(columns=["geometry", "index_right"], errors="ignore")

    return result


def process_region_year(region_name, year, ocean_gdf):
    input_path = os.path.join(INPUT_DIR, f"ais_{region_name}_20{year}.parquet")
    output_path = os.path.join(OUTPUT_DIR, f"ais_{region_name}_20{year}_ocean.parquet")

    if not os.path.exists(input_path):
        print(f"  ⚠ 跳过: 找不到 {input_path}")
        return 0, 0

    print(f"\\n{'=' * 60}")
    print(f"处理: {region_name} - 20{year}年")
    print(f"输入: {input_path}")
    print(f"输出: {output_path}")
    print(f"{'=' * 60}")

    pf = pq.ParquetFile(input_path)
    writer = None
    total_in = 0
    total_out = 0
    batch_count = 0

    for batch in pf.iter_batches(batch_size=BATCH_SIZE):
        batch_count += 1
        df = batch.to_pandas()
        total_in += len(df)

        filtered = filter_ocean_points_sjoin(df, ocean_gdf)
        total_out += len(filtered)

        if len(filtered) > 0:
            table = pa.Table.from_pandas(filtered, preserve_index=False)

            if writer is None:
                writer = pq.ParquetWriter(
                    output_path,
                    table.schema,
                    compression="zstd",
                    use_dictionary=True,
                )

            writer.write_table(table)
            del table

        rate = (1 - len(filtered) / len(df)) * 100 if len(df) > 0 else 0
        print(f"  [{batch_count:3d}] 输入 {len(df):>8,} → 海洋 {len(filtered):>8,} "
              f"(过滤 {rate:.1f}%)")

        del df, filtered
        gc.collect()

    if writer:
        writer.close()
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        keep_rate = total_out / total_in * 100 if total_in > 0 else 0
        print(f"  ✓ 完成: {total_in:,} → {total_out:,} (保留 {keep_rate:.1f}%) | {size_mb:.1f}MB")
    else:
        schema = pf.schema_arrow
        empty_table = schema.empty_table()
        pq.write_table(empty_table, output_path)
        print(f"  ⚠ 无海洋数据，写入空文件")

    return total_in, total_out


if __name__ == "__main__":
    grand_in = 0
    grand_out = 0

    for region_name in regions:
        ocean_gdf = load_ocean_polygon(region_name)

        for year in years:
            tin, tout = process_region_year(region_name, year, ocean_gdf)
            grand_in += tin
            grand_out += tout

    print(f"\\n{'=' * 60}")
    print("汇总报告")
    print(f"{'=' * 60}")
    print(f"  总输入:  {grand_in:>12,} 行")
    print(f"  总输出:  {grand_out:>12,} 行")
    print(f"  保留率:  {grand_out / grand_in * 100 if grand_in > 0 else 0:.1f}%")
    print(f"{'=' * 60}")
