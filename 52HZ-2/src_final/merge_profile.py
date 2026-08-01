"""
综合风险表
===========================
从 ais_indicators.csv (过滤 n≥5000) + sanctions_matrix.csv + 船舶档案
合并输出一份综合 CSV，供分析和 PPT 使用
"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent.parent / "src_final"))

import pandas as pd
import numpy as np
from pathlib import Path
from datalib_final import get_ship_archive

ROOT = Path(__file__).parent.parent
OUTPUT = ROOT / "output_final"

# ---- 加载各数据源 ----
print("[1] 加载数据...")
indicators = pd.read_csv(OUTPUT / "ais_indicators.csv")
matrix = pd.read_csv(OUTPUT / "sanctions_matrix.csv")
flag_risk = pd.read_csv(OUTPUT / "flag_risk_scores.csv")
archive = get_ship_archive()

# ---- 2. 从船舶档案提取有用字段 ----
print("[2] 提取船舶档案...")
archive_fields = {}
for _, row in archive._df.iterrows():
    m = row.get("ship_mmsi")
    if pd.isna(m):
        continue
    archive_fields[int(m)] = {
        "imo": str(row.get("ship_imo", "")).strip(),
        "build_year": row.get("ship_build_year"),
        "ship_type": str(row.get("ship_type", "")).strip(),
        "deadweight": row.get("ship_dead"),
        "builder": str(row.get("ship_builder_name", "")).strip(),
        "builder_country": str(row.get("ship_builder_country_name", "")).strip(),
    }

# ---- 3. 合并 ----
print("[3] 合并...")

# 统一 mmsi 类型
indicators["mmsi"] = indicators["mmsi"].astype("Int64")
matrix["mmsi"] = pd.to_numeric(matrix["mmsi"], errors="coerce").astype("Int64")

# 从 sanctions_matrix 取制裁详细列
sanction_cols = ["mmsi", "imo", "sanction_sources", "risk_level",
                 "hit_ofac", "hit_un", "hit_eu", "hit_uk", "sanction_detail"]
available_s = [c for c in sanction_cols if c in matrix.columns]
matrix_sub = matrix[available_s].copy()
matrix_sub = matrix_sub.drop_duplicates(subset=["mmsi"])

# 合并制裁
df = indicators.merge(matrix_sub, on="mmsi", how="left", suffixes=("", "_dup"))

# 合并船旗
flag_cols = ["mmsi", "flag_score", "paris_list", "tokyo_list", "flag_detail"]
flag_risk["mmsi"] = pd.to_numeric(flag_risk["mmsi"], errors="coerce").astype("Int64")
df = df.merge(flag_risk[flag_cols], on="mmsi", how="left", suffixes=("", "_flag"))

# ---- 3.5 合并未来指标（数据到后自动生效） ----
future_sources = {
    "ais_v2": {
        "path": OUTPUT / "ais_indicators_v3.csv",
        "cols": ["msr","spc","sdr","port_dwell","port_interval","turn_nonport","san_port_dwell","san_of_port"],
        "defaults": {"msr":0,"spc":0,"sdr":0,"port_dwell":0,"port_interval":0,"turn_nonport":0,"san_port_dwell":0,"san_of_port":0},
    },
    "identity": {
        "path": OUTPUT / "identity_changes.csv",
        "cols": ["name_changes", "flag_changes", "owner_changes", "total_identity_changes"],
        "defaults": {"name_changes": 0, "flag_changes": 0, "owner_changes": 0, "total_identity_changes": 0},
    },
    "port_call": {
        "path": OUTPUT / "port_call_anomaly.csv",
        "cols": ["recorded_calls", "unrecorded_call_ratio"],
        "defaults": {"recorded_calls": 0, "unrecorded_call_ratio": 0.0},
    },
    "hotspot": {
        "path": OUTPUT / "hotspot_dwell.csv",
        "cols": ["hotspot_dwell_ratio"],
        "defaults": {"hotspot_dwell_ratio": 0.0},
    },
}

for name, cfg in future_sources.items():
    if cfg["path"].exists():
        print(f"  [合并] {name}...")
        extra = pd.read_csv(cfg["path"])
        extra["mmsi"] = pd.to_numeric(extra["mmsi"], errors="coerce").astype("Int64")
        available_extra = ["mmsi"] + [c for c in cfg["cols"] if c in extra.columns]
        df = df.merge(extra[available_extra], on="mmsi", how="left")
        for c in cfg["cols"]:
            if c in df.columns:
                df[c] = df[c].fillna(cfg["defaults"].get(c, 0))
    else:
        for c in cfg["cols"]:
            df[c] = cfg["defaults"].get(c, 0)

# 如果 sanctions_matrix 也有 imo，保留它的
if "imo_dup" in df.columns:
    df["imo"] = df["imo_dup"].fillna(df.get("imo", ""))
    df = df.drop(columns=["imo_dup"])

# ---- 3.6 置信度（数据充分性评级） ----
print("[3.6] 置信度评级...")
n_median = df["n_points"].median()
d_median = df["total_days"].median()
df["data_sufficiency"] = (
    np.minimum(df["n_points"] / n_median, 1.0) * 0.5 +
    np.minimum(df["total_days"] / d_median, 1.0) * 0.5
).round(3)
def grade_conf(val):
    if val >= 0.8: return "A"
    if val >= 0.5: return "B"
    return "C"
df["confidence_grade"] = df["data_sufficiency"].apply(grade_conf)

# ---- 4. 补充船舶档案字段 ----
print("[4] 补充船舶档案 + age_risk...")
for field in ["build_year", "ship_type", "deadweight", "builder", "builder_country"]:
    df[field] = df["mmsi"].apply(
        lambda m: archive_fields.get(m, {}).get(field) if pd.notna(m) else None
    )

# age_risk: 文献中影子船队平均 20-25 年
def calc_age_risk(y):
    if pd.isna(y) or y == 0: return 0
    y = int(y)
    if y <= 2001: return 3      # ≥25年 → 高分
    if y <= 2006: return 2      # 20-25年
    if y <= 2011: return 1      # 15-20年（数据已限定 ≥15yr）
    return 0
df["age_risk"] = df["build_year"].apply(calc_age_risk)

# ---- 5. 过滤 n≥5000 ----
print("[5] 过滤 n ≥ 5000...")
before = len(df)
df = df[df["n_points"] >= 5000].copy()
print(f"  筛掉: {before - len(df)} 艘, 保留: {len(df)} 艘")

# ---- 6. 选择输出列，排好顺序 ----
print("[6] 整理列...")
out_cols = [
    # 基础信息
    "mmsi", "imo", "ship_name", "country", "operator",
    "build_year", "ship_type", "deadweight",
    "builder", "builder_country", "age_risk",
    # AIS 统计
    "n_points", "total_days",
    # 制裁
    "sanction_sources", "risk_level",
    "hit_ofac", "hit_un", "hit_eu", "hit_uk",
    # 船旗
    "flag_score", "paris_list", "tokyo_list",
    # 指标1 — Gap（主: ≥24h, 辅: 12h/72h counts）
    "gap_24h_ratio", "gap_24h_ci95_lower", "gap_24h_ci95_upper",
    "gap_24h_ci90_lower", "gap_24h_ci90_upper",
    "gap_24h_ci80_lower", "gap_24h_ci80_upper",
    "gap_12h_count", "gap_24h_count", "gap_72h_count",
    "gap_max_hours", "gap_mean_hours",
    # 指标2 — 速度异常
    "low_speed_ratio",
    "non_anch_low_ratio", "non_anch_low_ci95_lower", "non_anch_low_ci95_upper",
    "non_anch_low_ci90_lower", "non_anch_low_ci90_upper",
    "non_anch_low_ci80_lower", "non_anch_low_ci80_upper",
    "non_anch_low_events", "non_anch_low_max_dur_h",
    "loitering_h_ratio",
    # 指标1.5 — v2 行为指标 (针对活跃运输型影子船)
    "msr", "spc", "sdr", "port_dwell", "port_interval", "turn_nonport", "san_port_dwell", "san_of_port",
    # 指标3 — COG
    "cog_high_vol_ratio", "cog_high_vol_ci95_lower", "cog_high_vol_ci95_upper",
    "cog_high_vol_ci90_lower", "cog_high_vol_ci90_upper",
    "cog_high_vol_ci80_lower", "cog_high_vol_ci80_upper",
    "cog_very_high_vol_ratio",
    "cog_mean_vol", "cog_max_vol",
    # 综合
    "anomaly_index",
    "anomaly_ci95_lower", "anomaly_ci95_upper",
    "anomaly_ci90_lower", "anomaly_ci90_upper",
    "anomaly_ci80_lower", "anomaly_ci80_upper",
    "data_sufficiency", "confidence_grade",
    # 指标4-6（预留）
    "name_changes", "flag_changes", "owner_changes", "total_identity_changes",
    "recorded_calls", "unrecorded_call_ratio",
    "hotspot_dwell_ratio",
]

available = [c for c in out_cols if c in df.columns]
df = df[available]

# 排序
df = df.sort_values("anomaly_index", ascending=False)

# ---- 7. 保存 ----
out_path = OUTPUT / "vessel_risk_profile.csv"
df.to_csv(out_path, index=False, encoding="utf-8-sig")
print(f"\n[保存] {out_path}")
print(f"  {len(df)} 行 × {len(available)} 列")
print(f"\n列清单:")
for c in available:
    print(f"  {c}")
