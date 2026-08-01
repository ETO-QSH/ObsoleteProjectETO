"""
脚本1: AIS 数据清洗
===================
读取 ais_final_2026.parquet → 剔除坏坐标/陆地 → 按 MMSI 排序 → 写入 ais_clean_2026.parquet
"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent.parent / "src_final"))

import pandas as pd
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
from pathlib import Path
from collections import defaultdict
import time
import warnings
warnings.filterwarnings('ignore')

try:
    from global_land_mask import globe
    HAS_LAND_MASK = True
except ImportError:
    HAS_LAND_MASK = False
    print("[警告] global_land_mask 未安装，跳过陆地过滤。pip install global_land_mask")

ROOT = Path(__file__).parent.parent
DATABASE = ROOT / "database"
PARQUET_IN = DATABASE / "ais_final_2026.parquet"
PARQUET_OUT = DATABASE / "ais_clean_2026.parquet"


def main():
    t0 = time.time()
    print("=" * 60, flush=True)
    print("AIS 数据清洗", flush=True)
    print(f"  输入: {PARQUET_IN}", flush=True)
    print(f"  输出: {PARQUET_OUT}", flush=True)
    print(f"  陆地过滤: {'已启用' if HAS_LAND_MASK else '未启用'}", flush=True)
    print("=" * 60, flush=True)

    # ---- 第一遍：收集数据 ----
    print("\n[1/3] 遍历原始数据...", flush=True)
    pf = pq.ParquetFile(str(PARQUET_IN))
    cols = ["mmsi", "acqtime", "speed_knots", "cog_deg", "longitude", "latitude"]
    accum = defaultdict(lambda: {"ts": [], "sp": [], "cg": [], "ln": [], "lt": []})

    total_rows = 0
    bad_coords = 0
    land_filtered = 0
    batch_n = 0
    t1 = time.time()
    total_batches = pf.metadata.num_rows / 200_000

    for batch in pf.iter_batches(batch_size=200_000, columns=cols):
        df = batch.to_pandas()
        batch_n += 1
        raw = len(df)

        # 剔除越界坐标
        valid = (
            (df["latitude"] >= -90) & (df["latitude"] <= 90) &
            (df["longitude"] >= -180) & (df["longitude"] <= 180)
        )
        bad_coords += raw - valid.sum()
        df = df[valid]

        # 剔除陆地
        if HAS_LAND_MASK:
            before = len(df)
            land = globe.is_land(df["latitude"].values, df["longitude"].values)
            df = df[~land]
            land_filtered += before - len(df)

        total_rows += len(df)

        # 累积到 dict
        for mmsi, grp in df.groupby("mmsi"):
            m = int(mmsi)
            accum[m]["ts"].extend(grp["acqtime"].values)
            accum[m]["sp"].extend(grp["speed_knots"].values)
            accum[m]["cg"].extend(grp["cog_deg"].values)
            accum[m]["ln"].extend(grp["longitude"].values)
            accum[m]["lt"].extend(grp["latitude"].values)

        if batch_n % 15 == 0:
            pct = min(100, batch_n / total_batches * 100)
            print(f"  [{pct:3.0f}%] {total_rows:>12,} 行 | 坏坐标:{bad_coords:,} 陆地:{land_filtered:,} | {time.time()-t1:.0f}s", flush=True)

        del df, batch

    print(f"  [100%] {total_rows:>12,} 行 | 坏坐标:{bad_coords:,} 陆地:{land_filtered:,} | {time.time()-t1:.0f}s", flush=True)
    print(f"  唯一 MMSI: {len(accum)}", flush=True)

    # ---- 第二遍：按 MMSI 排序写入 Parquet ----
    print(f"\n[2/3] 写入清洁 Parquet（按 MMSI 排序）...", flush=True)
    schema = pa.schema([
        ("mmsi", pa.int64()),
        ("acqtime", pa.timestamp('ns', tz='UTC')),
        ("longitude", pa.float64()),
        ("latitude", pa.float64()),
        ("speed_knots", pa.float64()),
        ("cog_deg", pa.float64()),
    ])

    written = 0
    with pq.ParquetWriter(PARQUET_OUT, schema, compression="zstd") as writer:
        for mmsi in sorted(accum.keys()):
            data = accum[mmsi]
            n = len(data["ts"])
            ts = np.array(data["ts"])
            order = np.argsort(ts)

            table = pa.table({
                "mmsi": pa.array(np.full(n, mmsi, dtype=np.int64)),
                "acqtime": pa.array(ts[order], type=pa.timestamp('ns', tz='UTC')),
                "longitude": pa.array(np.array(data["ln"])[order], type=pa.float64()),
                "latitude": pa.array(np.array(data["lt"])[order], type=pa.float64()),
                "speed_knots": pa.array(np.array(data["sp"])[order]),
                "cog_deg": pa.array(np.array(data["cg"])[order]),
            })
            writer.write_table(table)
            written += 1
            if written % 100 == 0:
                print(f"  {written}/{len(accum)} MMSI", flush=True)
        print(f"  {written}/{len(accum)} MMSI", flush=True)

    accum.clear()
    size_mb = PARQUET_OUT.stat().st_size / 1024**2
    print(f"\n[3/3] 完成", flush=True)
    print(f"  输出: {PARQUET_OUT} ({size_mb:.0f} MB)", flush=True)
    print(f"  保留: {total_rows:,} 行（剔除坏坐标 {bad_coords:,}, 陆地 {land_filtered:,}）", flush=True)
    print(f"  总耗时: {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
