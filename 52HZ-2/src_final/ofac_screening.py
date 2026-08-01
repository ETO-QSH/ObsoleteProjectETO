"""
OFAC SDN 制裁名单筛查 — 修复版
=====================================
SDN CSV 格式（无header，12列）:
  0: sdn_number    1: sdn_name      2: sdn_type       3: sdn_program
  4: sdn_title     5: sdn_address   6: sdn_city       7: sdn_state
  8: sdn_postal    9: sdn_country   10: sdn_remarks   11: sdn_extra (含IMO)
"""

import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent.parent / "src_final"))

import pandas as pd
import re
import time
from pathlib import Path
from io import StringIO
from datalib_final import get_ship_archive, get_all_mmsi

ROOT = Path(__file__).parent.parent
OUTPUT = ROOT / "output_final"
EXTERNAL = ROOT / "external_final" / "OFAC SDN 制裁名单"
SDN_CSV = EXTERNAL / "sdn.csv"
OUTPUT.mkdir(parents=True, exist_ok=True)

SDN_COLS = [
    "sdn_number", "sdn_name", "sdn_type", "sdn_program",
    "sdn_title", "sdn_address", "sdn_city", "sdn_state",
    "sdn_postal", "sdn_country", "sdn_remarks", "sdn_extra",
]


def norm(s):
    if pd.isna(s) or not s:
        return ""
    s = str(s).lower().strip()
    s = re.sub(r'[^\w\s]', '', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def build_targets():
    archive = get_ship_archive()
    archive_df = archive._df
    ais_mmsi = set(get_all_mmsi())
    archive_mmsi = archive.get_mmsi_set()
    ais_only = ais_mmsi - archive_mmsi
    print(f"[1] 待匹配: 档案 {len(archive_df)} + AIS独有 {len(ais_only)} = {len(archive_df)+len(ais_only)}")

    records = []
    for _, row in archive_df.iterrows():
        mmsi = row.get("ship_mmsi")
        if pd.isna(mmsi):
            continue
        imo_raw = str(row.get("ship_imo", ""))
        # 提取纯数字 IMO
        imo_clean = ""
        m = re.search(r'\b(\d{7})\b', imo_raw)
        if m:
            imo_clean = m.group(1)
        records.append({
            "mmsi": int(mmsi),
            "ship_name": str(row.get("ship_name", "")).strip(),
            "imo": imo_clean,
            "country": str(row.get("ship_country_name", "")).strip(),
            "build_year": row.get("ship_build_year"),
            "ship_type": str(row.get("ship_type", "")).strip(),
            "operator": str(row.get("operator_name", "")).strip(),
            "builder": str(row.get("ship_builder_name", "")).strip(),
            "deadweight": row.get("ship_dead"),
            "source": "archive",
        })
    for mmsi in sorted(ais_only):
        records.append({
            "mmsi": mmsi, "ship_name": "", "imo": "",
            "country": "", "build_year": None, "ship_type": "",
            "operator": "", "builder": "", "deadweight": None,
            "source": "ais_only",
        })
    return pd.DataFrame(records)


def load_sdn(filepath: Path):
    print(f"[2] 加载 SDN: {filepath}")
    t0 = time.time()

    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        raw = f.read()

    # 去掉注释行
    data_lines = [line for line in raw.split('\n')
                  if not line.startswith('#') and line.strip()]

    df = pd.read_csv(StringIO('\n'.join(data_lines)), header=None, low_memory=False)
    df.columns = SDN_COLS[:len(df.columns)]
    print(f"  SDN 条目: {len(df):,} (加载 {time.time()-t0:.1f}s)")

    # 统计 vessel
    vessel_count = df["sdn_type"].astype(str).str.lower().str.contains('vessel').sum()
    print(f"  其中 vessel: {vessel_count}")

    # ---- 构建 IMO/MMSI 倒排索引（从 sdn_extra 列提取）----
    t1 = time.time()
    imo_idx = {}
    mmsi_idx = {}

    for i in range(len(df)):
        extra = str(df.iloc[i]["sdn_extra"]) if "sdn_extra" in df.columns else ""
        name = str(df.iloc[i]["sdn_name"]) if "sdn_name" in df.columns else ""
        # 合并 name + remarks + extra 用于搜索
        full = f"{name} {extra}"

        for imo in re.findall(r'IMO[:\s]*(\d{7})', full, re.IGNORECASE):
            imo_idx.setdefault(imo, set()).add(i)
        # 也匹配纯数字7位（在 vessel 上下文中）
        if 'vessel' in str(df.iloc[i]["sdn_type"]).lower():
            for imo in re.findall(r'\b(\d{7})\b', extra):
                imo_idx.setdefault(imo, set()).add(i)

        for mmsi in re.findall(r'MMSI[:\s]*(\d{9})', full, re.IGNORECASE):
            mmsi_idx.setdefault(mmsi, set()).add(i)

    print(f"  IMO 索引: {len(imo_idx)} 个 | MMSI 索引: {len(mmsi_idx)} 个")
    print(f"  索引耗时: {time.time()-t1:.1f}s")

    return df, imo_idx, mmsi_idx


def match_indexed(targets, sdn_df, imo_idx, mmsi_idx):
    print(f"[3] 匹配 {len(targets)} 艘船...")
    t0 = time.time()

    matches = []
    imo_hits = 0
    mmsi_hits = 0

    for _, ship in targets.iterrows():
        ship_imo = str(ship["imo"]).strip()
        ship_mmsi = str(int(ship["mmsi"]))
        ship_name = str(ship["ship_name"]).strip()

        best_score = 0
        best_sdn_idx = -1
        best_reasons = []

        # --- IMO 精确命中 ---
        if ship_imo and ship_imo in imo_idx:
            imo_hits += 1
            sdn_i = next(iter(imo_idx[ship_imo]))  # 取第一个
            best_score = 100
            best_sdn_idx = sdn_i
            best_reasons = [f"IMO={ship_imo}"]

        # --- MMSI 精确命中 ---
        if best_score < 100 and ship_mmsi and ship_mmsi in mmsi_idx:
            mmsi_hits += 1
            sdn_i = next(iter(mmsi_idx[ship_mmsi]))
            score = 90
            if score > best_score:
                best_score = score
                best_sdn_idx = sdn_i
                best_reasons = [f"MMSI={ship_mmsi}"]

        # --- 名称模糊匹配：跳过（IMO/MMSI 索引已足够覆盖，且 500+×19000 太慢）---
        # 如需启用，取消下面注释
        # if best_score < 50 and ship_name:
        #     ship_n = norm(ship_name)
        #     ...

        # --- 记录 ---
        if best_score >= 25:
            sdn_row = sdn_df.iloc[best_sdn_idx]
            matches.append({
                "mmsi": ship["mmsi"],
                "ship_name": ship_name,
                "imo": ship_imo,
                "country": ship["country"],
                "operator": ship["operator"],
                "build_year": ship["build_year"],
                "ship_type": ship["ship_type"],
                "deadweight": ship["deadweight"],
                "source": ship["source"],
                "match_score": best_score,
                "match_reason": "; ".join(best_reasons),
                "sdn_number": str(sdn_row.get("sdn_number", "")),
                "sdn_name": str(sdn_row.get("sdn_name", "")),
                "sdn_type": str(sdn_row.get("sdn_type", "")),
                "sdn_program": str(sdn_row.get("sdn_program", "")),
                "sdn_country": str(sdn_row.get("sdn_country", "")),
                "sdn_remarks": str(sdn_row.get("sdn_remarks", "")),
                "sdn_extra": str(sdn_row.get("sdn_extra", ""))[:300],
            })

    result = pd.DataFrame(matches)
    if not result.empty:
        result = result.sort_values("match_score", ascending=False)

    print(f"  完成 ({time.time()-t0:.1f}s) | IMO命中:{imo_hits} MMSI命中:{mmsi_hits}")
    print(f"  匹配: {len(result)} 艘")
    return result


if __name__ == "__main__":
    print("=" * 60)
    print("OFAC SDN 筛查")
    print("=" * 60)

    if not SDN_CSV.exists():
        print(f"SDN CSV 未找到: {SDN_CSV}")
        sys.exit(1)

    targets = build_targets()
    sdn_df, imo_idx, mmsi_idx = load_sdn(SDN_CSV)
    matches = match_indexed(targets, sdn_df, imo_idx, mmsi_idx)

    output_path = OUTPUT / "ofac_sdn_matches.csv"
    matches.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"\n[保存] {output_path}")

    # 报告
    print("\n" + "=" * 60)
    print("匹配结果")
    print("=" * 60)
    if matches.empty:
        print("无命中")
    else:
        high = matches[matches["match_score"] >= 50]
        med = matches[(matches["match_score"] >= 25) & (matches["match_score"] < 50)]
        print(f"  高置信度(≥50): {len(high)} | 中置信度(25-49): {len(med)} | 总计: {len(matches)}")

        # 按制裁项目分组
        if "sdn_program" in matches.columns:
            prog_counts = matches["sdn_program"].value_counts()
            print(f"\n  制裁项目分布:")
            for prog, cnt in prog_counts.head(15).items():
                print(f"    {prog}: {cnt}")

        print(f"\n--- 前20条高置信度 ---")
        for _, r in high.head(20).iterrows():
            print(f"  [{r['match_score']:.0f}] {r['ship_name']}")
            print(f"    MMSI={r['mmsi']} IMO={r['imo']} | {r['country']}")
            print(f"    SDN: {r['sdn_name']} | 类型:{r['sdn_type']} | 项目:{r['sdn_program']}")
            print(f"    原因: {r['match_reason']}")

    archive_hit = matches[matches["source"]=="archive"] if not matches.empty else matches
    ais_hit = matches[matches["source"]=="ais_only"] if not matches.empty else matches
    print(f"\n档案命中: {len(archive_hit)} | AIS独有命中: {len(ais_hit)}")
    print("完成")
