"""
脚本2: AIS 异常指标计算
=======================
读取 ais_clean_2026.parquet → 逐船计算三个指标 → 输出 ais_indicators.csv

依赖: 脚本1 (clean_ais.py) 已生成 ais_clean_2026.parquet
"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent.parent / "src_final"))

import pandas as pd
import numpy as np
import geopandas as gpd
import pyarrow.parquet as pq
from pathlib import Path
from shapely.geometry import Point
from shapely import prepared
import time
import warnings
warnings.filterwarnings('ignore')

ROOT = Path(__file__).parent.parent
OUTPUT = ROOT / "output_final"
DATABASE = ROOT / "database"
PARQUET_CLEAN = DATABASE / "ais_clean_2026.parquet"
OIL_PORTS_CSV = ROOT / "决赛资料" / "原油装卸港清单" / "原油装卸港清单_详细.csv"


# ============================================================
# 1. 构建锚地区域（25km buffer，279 个原油港口）
# ============================================================

def build_anchorage_zones():
    print("[锚地] 加载原油港口坐标...", flush=True)
    oil = pd.read_csv(OIL_PORTS_CSV)
    oil = oil[oil['lat'].notna() & (oil['lat'] != '')].copy()
    oil['lat'] = pd.to_numeric(oil['lat'], errors='coerce')
    oil['lon'] = pd.to_numeric(oil['lon'], errors='coerce')
    oil = oil.dropna(subset=['lat', 'lon'])
    print(f"[锚地] 加载 {len(oil)} 个港口坐标", flush=True)

    from shapely.geometry import Point as SPt
    geoms = [SPt(r['lon'], r['lat']) for _, r in oil.iterrows()]
    gs = gpd.GeoSeries(geoms, crs="EPSG:4326").to_crs("EPSG:3857")
    gs_buf = gs.buffer(25000)
    gs_buf = gs_buf.to_crs("EPSG:4326")
    anch = prepared.prep(gs_buf.union_all())
    print(f"[锚地] 构建完成（25km buffer）", flush=True)
    return anch


# ============================================================
# 2. 单船指标计算
# ============================================================

def compute_indicators(timestamps, speeds, cogs, lons, lats, anchorage):
    n = len(timestamps)
    if n < 2:
        return _empty()

    WEIGHTS = {"gap": 25, "speed": 30, "cog": 20, "loiter": 15, "age": 10}

    # ---- 指标1: AIS Gap（主指标: 24h，文献阈值）----
    gaps_h = np.diff(timestamps.astype("int64")) / 1e9 / 3600
    gap_12h = int(np.sum(gaps_h > 12))
    gap_24h = int(np.sum(gaps_h > 24))
    gap_72h = int(np.sum(gaps_h > 72))
    gap_max = float(np.max(gaps_h)) if len(gaps_h) > 0 else 0.0
    gap_mean = float(np.mean(gaps_h)) if len(gaps_h) > 0 else 0.0
    n_gaps = len(gaps_h)
    gap_ci = wilson_multi(gap_24h, n_gaps)  # 主指标: 24h
    total_days = (timestamps[-1].astype("int64") - timestamps[0].astype("int64")) / 1e9 / 86400
    total_days = max(total_days, 0.01)

    # ---- 指标2: 速度异常 ----
    low_mask = speeds < 1.0
    in_anch = np.zeros(n, dtype=bool)
    chunk = 5000
    for i in range(0, n, chunk):
        end = min(i + chunk, n)
        pts = [Point(lons[j], lats[j]) for j in range(i, end)]
        in_anch[i:end] = [anchorage.contains(p) for p in pts]

    non_anch_low = low_mask & (~in_anch)
    non_anch_low_count = int(np.sum(non_anch_low))
    speed_ci = wilson_multi(non_anch_low_count, n)

    events = 0; max_dur_pts = 0; cur = 0
    for i in range(n):
        if non_anch_low[i]:
            cur += 1
        else:
            if cur > 0: events += 1; max_dur_pts = max(max_dur_pts, cur); cur = 0
    if cur > 0: events += 1; max_dur_pts = max(max_dur_pts, cur)
    max_dur_h = max_dur_pts * gap_mean if gap_mean > 0 else max_dur_pts

    # ---- 指标3: COG 波动 ----
    W = 5; vols = []
    for i in range(n - W + 1):
        wc = cogs[i:i+W]
        sin_s = np.sum(np.sin(np.radians(wc))); cos_s = np.sum(np.cos(np.radians(wc)))
        R = np.sqrt(sin_s**2 + cos_s**2) / W
        if R < 0.001:      std_d = 180.0
        elif R >= 1.0:      std_d = 0.0
        else:               std_d = float(np.degrees(np.sqrt(-2 * np.log(R)))); std_d = min(std_d, 180.0)
        vols.append(std_d)

    vol = np.array(vols); n_vol = len(vol)
    high_count = int(np.sum(vol > 30)); vhigh_count = int(np.sum(vol > 60))
    cog_ci = wilson_multi(high_count, n_vol)
    _, _, vhigh_ratio = wilson_multi(vhigh_count, n_vol)["ci95"]
    mean_vol = round(float(np.mean(vol)), 2) if n_vol > 0 else 0.0
    max_vol = round(float(np.max(vol)), 2) if n_vol > 0 else 0.0

    # ---- 综合 anomaly + 三级 CI 传播 ----
    # loitering_h_ratio = 非锚地低速总估算时长 / 总观测时长
    loiter_h = non_anch_low_count * gap_mean if gap_mean > 0 and non_anch_low_count > 0 else 0
    loiter_ratio = round(loiter_h / (total_days * 24), 6) if total_days > 0 else 0.0

    anomaly = (gap_ci["ci95"][2] * WEIGHTS["gap"] +
               speed_ci["ci95"][2] * WEIGHTS["speed"] +
               cog_ci["ci95"][2] * WEIGHTS["cog"] +
               loiter_ratio * WEIGHTS["loiter"])

    out = {
        "n_points": n, "total_days": round(total_days, 1),
        # 指标1: Gap（主: ≥24h）
        "gap_24h_ratio": gap_ci["ci95"][2],
        "gap_12h_count": gap_12h, "gap_24h_count": gap_24h, "gap_72h_count": gap_72h,
        "gap_max_hours": round(gap_max, 1), "gap_mean_hours": round(gap_mean, 1),
        # 指标2: 速度
        "low_speed_ratio": round(float(np.sum(low_mask)) / n, 6),
        "non_anch_low_ratio": speed_ci["ci95"][2],
        "non_anch_low_events": events, "non_anch_low_max_dur_h": round(max_dur_h, 1),
        "loitering_h_ratio": loiter_ratio,
        # 指标3: COG
        "cog_high_vol_ratio": cog_ci["ci95"][2],
        "cog_very_high_vol_ratio": vhigh_ratio,
        "cog_mean_vol": mean_vol, "cog_max_vol": max_vol,
        "anomaly_index": round(anomaly, 2),
    }

    for label in ["ci95", "ci90", "ci80"]:
        for prefix, ci in [("gap_24h", gap_ci), ("non_anch_low", speed_ci), ("cog_high_vol", cog_ci)]:
            out[f"{prefix}_{label}_lower"] = ci[label][0]
            out[f"{prefix}_{label}_upper"] = ci[label][1]
        alo = (gap_ci[label][0] * WEIGHTS["gap"] +
               speed_ci[label][0] * WEIGHTS["speed"] +
               cog_ci[label][0] * WEIGHTS["cog"] +
               loiter_ratio * WEIGHTS["loiter"])
        ahi = (gap_ci[label][1] * WEIGHTS["gap"] +
               speed_ci[label][1] * WEIGHTS["speed"] +
               cog_ci[label][1] * WEIGHTS["cog"] +
               loiter_ratio * WEIGHTS["loiter"])
        out[f"anomaly_{label}_lower"] = round(alo, 2)
        out[f"anomaly_{label}_upper"] = round(ahi, 2)

    return out


def _empty():
    ci_cols = []
    for pfx in ["gap_24h", "non_anch_low", "cog_high_vol", "anomaly"]:
        for lvl in ["ci95", "ci90", "ci80"]:
            ci_cols += [f"{pfx}_{lvl}_lower", f"{pfx}_{lvl}_upper"]
    base = {
        "n_points": 0, "total_days": 0,
        "gap_24h_ratio": 0, "gap_12h_count": 0, "gap_24h_count": 0, "gap_72h_count": 0,
        "gap_max_hours": 0, "gap_mean_hours": 0,
        "low_speed_ratio": 0, "non_anch_low_ratio": 0,
        "non_anch_low_events": 0, "non_anch_low_max_dur_h": 0,
        "loitering_h_ratio": 0,
        "cog_high_vol_ratio": 0, "cog_very_high_vol_ratio": 0,
        "cog_mean_vol": 0, "cog_max_vol": 0,
        "anomaly_index": 0,
    }
    for c in ci_cols:
        base[c] = 0.0
    return base


def wilson_multi(successes: int, total: int):
    """Wilson score interval at 95%, 90%, 80% confidence levels.
    Returns {ci95: (lower, upper, center), ci90: (...), ci80: (...)}"""
    if total == 0:
        zero = (0.0, 0.0, 0.0)
        return {"ci95": zero, "ci90": zero, "ci80": zero}
    p = successes / total
    n = total
    result = {}
    for label, z in [("ci95", 1.96), ("ci90", 1.645), ("ci80", 1.282)]:
        z2 = z * z
        center = (p + z2 / (2 * n)) / (1 + z2 / n)
        margin = z / (1 + z2 / n) * np.sqrt(p * (1 - p) / n + z2 / (4 * n * n))
        lower = max(0.0, center - margin)
        upper = min(1.0, center + margin)
        result[label] = (round(lower, 6), round(upper, 6), round(center, 6))
    return result


# ============================================================
# 3. 主流程
# ============================================================

def main():
    from datalib_final import get_ship_archive

    t_total = time.time()
    print("=" * 60, flush=True)
    print("AIS 异常指标计算", flush=True)
    print(f"  数据源: {PARQUET_CLEAN}", flush=True)
    print("=" * 60, flush=True)

    if not PARQUET_CLEAN.exists():
        print(f"\n[错误] 未找到 {PARQUET_CLEAN}", flush=True)
        print("请先运行 clean_ais.py", flush=True)
        sys.exit(1)

    anchorage = build_anchorage_zones()

    # ---- 获取 MMSI 列表 ----
    pf = pq.ParquetFile(str(PARQUET_CLEAN))
    # 从 row group metadata 提取所有 mmsi
    all_mmsi = set()
    for rg in range(pf.metadata.num_row_groups):
        rg_meta = pf.metadata.row_group(rg)
        for col in range(rg_meta.num_columns):
            if rg_meta.column(col).path_in_schema == "mmsi":
                stats = rg_meta.column(col).statistics
                if stats and stats.min is not None:
                    all_mmsi.add(int(stats.min))
                    all_mmsi.add(int(stats.max))
    mmsi_list = sorted(all_mmsi)
    total = len(mmsi_list)
    print(f"\n[计算] {total} 艘船，逐船计算指标...", flush=True)
    t2 = time.time()

    # ---- 预加载船名用于日志 ----
    archive = get_ship_archive()
    mmsi_name = {}
    for _, row in archive._df.iterrows():
        m = row.get("ship_mmsi")
        if pd.notna(m):
            mmsi_name[int(m)] = str(row.get("ship_name", "")).strip()[:20]

    results = []
    for idx, mmsi in enumerate(mmsi_list):
        # 读取单船数据
        tbl = pq.read_table(str(PARQUET_CLEAN), filters=[("mmsi", "=", mmsi)])
        df_ship = tbl.to_pandas()

        ts = df_ship["acqtime"].values
        sp = df_ship["speed_knots"].values
        cg = df_ship["cog_deg"].values
        ln = df_ship["longitude"].values
        lt = df_ship["latitude"].values

        ind = compute_indicators(ts, sp, cg, ln, lt, anchorage)
        ind["mmsi"] = mmsi
        results.append(ind)

        name = mmsi_name.get(mmsi, "?")
        pct = (idx + 1) / total * 100
        ela = time.time() - t2
        eta = ela / (idx + 1) * (total - idx - 1) if idx > 0 else 0
        print(f"  [{pct:3.0f}%] {idx+1}/{total} MMSI={mmsi} {name:20s} | "
              f"gap24={ind['gap_24h_ratio']:.4f} speed={ind['non_anch_low_ratio']:.3f} "
              f"cog={ind['cog_high_vol_ratio']:.3f} | {ela:.0f}s", flush=True)

        del df_ship, tbl

    df = pd.DataFrame(results)
    df = df[["mmsi"] + [c for c in df.columns if c != "mmsi"]]

    # ---- 合并元数据 ----
    print(f"\n[合并] 元数据...", flush=True)
    names, countries, operators = {}, {}, {}
    for _, row in archive._df.iterrows():
        m = row.get("ship_mmsi")
        if pd.notna(m):
            names[int(m)] = str(row.get("ship_name", "")).strip()
            countries[int(m)] = str(row.get("ship_country_name", "")).strip()
            operators[int(m)] = str(row.get("operator_name", "")).strip()

    df["ship_name"] = df["mmsi"].map(names).fillna("")
    df["country"] = df["mmsi"].map(countries).fillna("")
    df["operator"] = df["mmsi"].map(operators).fillna("")

    # 合并制裁矩阵
    matrix_path = OUTPUT / "sanctions_matrix.csv"
    if matrix_path.exists():
        matrix = pd.read_csv(matrix_path)
        matrix["mmsi"] = pd.to_numeric(matrix["mmsi"], errors="coerce").astype("Int64")
        df["mmsi_tmp"] = df["mmsi"].astype("Int64")
        meta_cols = ["mmsi", "sanction_sources", "risk_level", "flag_score",
                     "hit_ofac", "hit_un", "hit_eu", "hit_uk", "paris_list", "tokyo_list"]
        available = ["mmsi"] + [c for c in meta_cols[1:] if c in matrix.columns]
        meta = matrix[available].copy()
        meta.columns = ["mmsi_tmp"] + [c for c in meta.columns[1:]]
        df = df.merge(meta, on="mmsi_tmp", how="left")
        df = df.drop(columns=["mmsi_tmp"])

    df = df.sort_values("anomaly_index", ascending=False)

    # ---- 保存 ----
    OUTPUT.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT / "ais_indicators.csv"
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"\n[保存] {output_path}", flush=True)

    # ---- 报告 ----
    print(f"\n{'='*60}", flush=True)
    print(f"总耗时: {time.time()-t_total:.0f}s | 船只: {len(df)}", flush=True)

    print(f"\n指标1 — Gap > 12h:", flush=True)
    print(f"  有 Gap24: {(df['gap_24h_count']>0).sum()} 艘 | 均值: {df['gap_24h_ratio'].mean():.4f}", flush=True)
    for _, r in df.head(5).iterrows():
        print(f"  {r['ship_name'][:30]} | ratio={r['gap_24h_ratio']:.4f} | max={r['gap_max_hours']:.0f}h", flush=True)

    print(f"\n指标2 — 非锚地低速:", flush=True)
    print(f"  有事件: {(df['non_anch_low_events']>0).sum()} 艘 | 均值: {df['non_anch_low_ratio'].mean():.4f}", flush=True)
    for _, r in df.nlargest(5, "non_anch_low_ratio").iterrows():
        print(f"  {r['ship_name'][:30]} | ratio={r['non_anch_low_ratio']:.4f} | events={r['non_anch_low_events']}", flush=True)

    print(f"\n指标3 — COG 高波动:", flush=True)
    print(f"  有波动: {(df['cog_high_vol_ratio']>0).sum()} 艘 | 均值: {df['cog_high_vol_ratio'].mean():.4f}", flush=True)
    for _, r in df.nlargest(5, "cog_high_vol_ratio").iterrows():
        print(f"  {r['ship_name'][:30]} | ratio={r['cog_high_vol_ratio']:.4f} | mean_vol={r['cog_mean_vol']:.1f}°", flush=True)

    print("\n完成", flush=True)


if __name__ == "__main__":
    main()
