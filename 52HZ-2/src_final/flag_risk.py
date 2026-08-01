"""
船旗国风险打分（Paris MoU + Tokyo MoU）
======================================
基于 Paris MoU White/Grey/Black List 和 Tokyo MoU Flag Performance List
为每艘船分配船旗风险分（0-3），并合并到制裁矩阵
"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent.parent / "src_final"))

import pandas as pd
import json
from pathlib import Path
from datalib_final import get_ship_archive, get_all_mmsi

ROOT = Path(__file__).parent.parent
EXTERNAL = ROOT / "external_final" / "船旗国黑白名单"
OUTPUT = ROOT / "output_final"

# ============================================================
# 1. 加载 Paris MoU
# ============================================================

def load_paris() -> dict[str, dict]:
    """返回 {flag_name: {list, risk, excess_factor}}"""
    with open(EXTERNAL / "Paris MoU" / "Paris_MoU_2025_Performance_Lists.json", 'r', encoding='utf-8') as f:
        data = json.load(f)

    result = {}
    lists_data = data["lists"]

    for entry in lists_data["white_list"]["entries"]:
        result[_norm_flag(entry["flag"])] = {
            "paris_list": "White",
            "paris_risk": "Low",
            "paris_excess": entry["excess_factor"],
            "paris_rank": entry["rank"],
        }

    for entry in lists_data["grey_list"]["entries"]:
        result[_norm_flag(entry["flag"])] = {
            "paris_list": "Grey",
            "paris_risk": "Medium",
            "paris_excess": entry["excess_factor"],
            "paris_rank": entry["rank"],
        }

    for entry in lists_data["black_list"]["entries"]:
        result[_norm_flag(entry["flag"])] = {
            "paris_list": "Black",
            "paris_risk": entry.get("risk", "High"),
            "paris_excess": entry["excess_factor"],
            "paris_rank": entry["rank"],
        }

    print(f"[Paris MoU] {len(result)} flags loaded")
    return result


# ============================================================
# 2. 加载 Tokyo MoU
# ============================================================

def load_tokyo() -> dict[str, dict]:
    with open(EXTERNAL / "Tokyo MoU" / "Tokyo_MoU_Flag_Performance_List_2025.json", 'r', encoding='utf-8') as f:
        data = json.load(f)

    result = {}
    # Tokyo JSON: {lists: {high_performance: {description, entries: [...]}, ...}}
    lists = data.get("lists", data)  # 兼容有/无 lists 包裹
    for entry in lists.get("high_performance", {}).get("entries", []):
        result[_norm_flag(entry["flag"])] = {
            "tokyo_list": "High Performance",
            "tokyo_excess": entry["excess_factor"],
            "tokyo_rank": entry["rank"],
        }
    for entry in lists.get("medium_performance", {}).get("entries", []):
        result[_norm_flag(entry["flag"])] = {
            "tokyo_list": "Medium Performance",
            "tokyo_excess": entry["excess_factor"],
            "tokyo_rank": entry["rank"],
        }
    for entry in lists.get("low_performance", {}).get("entries", []):
        result[_norm_flag(entry["flag"])] = {
            "tokyo_list": "Low Performance",
            "tokyo_excess": entry["excess_factor"],
            "tokyo_rank": entry["rank"],
        }

    print(f"[Tokyo MoU] {len(result)} flags loaded")
    return result


# ============================================================
# 3. 归一化船旗名
# ============================================================

def _norm_flag(name: str) -> str:
    """统一船旗国名称"""
    name = name.strip().lower()
    # 去后缀
    for suffix in [', uk', ' (uk)', ', china', ' (china)', ', republic of']:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
    # 常见别名
    aliases = {
        'korea, republic of': 'south korea',
        'russian federation': 'russia',
        'taiwan, china': 'taiwan',
        'hong kong, china': 'hong kong',
        'türkiye': 'turkey',
        'viet nam': 'vietnam',
        'united states of america': 'united states',
        'united kingdom (uk)': 'united kingdom',
        'tanzania, united republic of': 'tanzania',
        'sao tome and principe': 'sao tome & principe',
    }
    return aliases.get(name, name).strip()


def normalize_country_for_match(name: str) -> str:
    """将船舶档案中的国家名归一化以匹配"""
    if pd.isna(name) or not name:
        return ""
    name = str(name).strip().lower()
    # 常见映射
    aliases = {
        'south korea': 'korea, republic of',
        'russia': 'russian federation',
        'taiwan': 'taiwan, china',
        'hong kong': 'hong kong, china',
        'vietnam': 'viet nam',
        'united states': 'united states of america',
        'united kingdom': 'united kingdom (uk)',
        'tanzania': 'tanzania, united republic of',
    }
    # 先尝试原始名称
    return aliases.get(name, name)


# ============================================================
# 4. 打分
# ============================================================

def score_flag(country: str, paris: dict, tokyo: dict) -> dict:
    """..."""
    if pd.isna(country) or not country:
        return {
            "flag_score": 0, "paris_list": "Unknown", "tokyo_list": "Unknown",
            "paris_risk": "", "flag_detail": "未知船旗"
        }
    key = _norm_flag(str(country))
    p = paris.get(key, {})
    t = tokyo.get(key, {})

    score = 0
    details = []

    # Paris MoU 评分
    paris_list = p.get("paris_list", "Not Listed")
    if paris_list == "Black":
        risk_label = p.get("paris_risk", "High")
        if "Very High" in risk_label:
            score = max(score, 3)
            details.append(f"Paris:Black({risk_label})")
        elif "Medium to High" in risk_label:
            score = max(score, 2)
            details.append(f"Paris:Black({risk_label})")
        else:
            score = max(score, 2)
            details.append(f"Paris:Black({risk_label})")
    elif paris_list == "Grey":
        score = max(score, 1)
        details.append("Paris:Grey")
    elif paris_list == "White":
        score = max(score, 0)
        details.append("Paris:White")

    # Tokyo MoU 评分
    tokyo_list = t.get("tokyo_list", "Not Listed")
    if tokyo_list == "Low Performance":
        score = max(score, 2)
        details.append(f"Tokyo:Low(EF={t.get('tokyo_excess',''):.1f})")
    elif tokyo_list == "Medium Performance":
        score = max(score, 1)
        details.append("Tokyo:Medium")
    elif tokyo_list == "High Performance":
        details.append("Tokyo:High")

    # 特殊：完全不在任何名单中
    if not details:
        details.append("未列入")

    return {
        "flag_score": score,
        "paris_list": paris_list,
        "tokyo_list": tokyo_list,
        "paris_risk": p.get("paris_risk", ""),
        "flag_detail": "; ".join(details),
    }


# ============================================================
# 5. 主流程
# ============================================================

def main():
    print("=" * 60)
    print("船旗国风险打分（Paris MoU + Tokyo MoU）")
    print("=" * 60)

    paris = load_paris()
    tokyo = load_tokyo()

    # 加载制裁矩阵
    matrix_path = OUTPUT / "sanctions_matrix.csv"
    if matrix_path.exists():
        df = pd.read_csv(matrix_path)
        print(f"\n[加载] 制裁矩阵: {len(df)} 条")
    else:
        print("\n制裁矩阵不存在，从原始数据构建...")
        archive = get_ship_archive()
        records = []
        ais_mmsi = set(get_all_mmsi())
        for _, row in archive._df.iterrows():
            mmsi = row.get("ship_mmsi")
            if pd.notna(mmsi):
                records.append({
                    "mmsi": int(mmsi),
                    "imo": None,
                    "ship_name": str(row.get("ship_name", "")).strip(),
                    "country": str(row.get("ship_country_name", "")).strip(),
                })
        for m in sorted(ais_mmsi - archive.get_mmsi_set()):
            records.append({"mmsi": m, "imo": None, "ship_name": "", "country": ""})
        df = pd.DataFrame(records)

    # 打分
    print(f"\n[打分] {len(df)} 艘船...")
    scores = []
    for _, row in df.iterrows():
        country = row.get("country", "")
        result = score_flag(country, paris, tokyo)
        scores.append(result)

    df["flag_score"] = [s["flag_score"] for s in scores]
    df["paris_list"] = [s["paris_list"] for s in scores]
    df["tokyo_list"] = [s["tokyo_list"] for s in scores]
    df["paris_risk"] = [s["paris_risk"] for s in scores]
    df["flag_detail"] = [s["flag_detail"] for s in scores]

    # 保存
    output_path = OUTPUT / "flag_risk_scores.csv"
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"[保存] {output_path}")

    # 统计
    print(f"\n{'='*60}")
    print("船旗国风险分布")
    print(f"{'='*60}")
    for s, label in [(3, "极高风险"), (2, "高风险"), (1, "中风险"), (0, "低风险/未列入")]:
        cnt = (df["flag_score"] == s).sum()
        pct = cnt / len(df) * 100
        print(f"  {label}: {cnt} ({pct:.1f}%)")

    # 重点：高风险船旗国详情
    high_risk = df[df["flag_score"] >= 2]
    if not high_risk.empty:
        print(f"\n高风险船旗详情 (flag_score ≥ 2):")
        country_counts = high_risk["country"].value_counts()
        for country, cnt in country_counts.items():
            sample = high_risk[high_risk["country"] == country].iloc[0]
            print(f"  {country}: {cnt}艘 — {sample['flag_detail']}")

    # 合并到制裁矩阵
    if matrix_path.exists():
        print(f"\n[合并] 将 flag_score 合并到制裁矩阵...")
        # 只保留需要的列
        flag_cols = df[["mmsi", "flag_score", "paris_list", "tokyo_list", "paris_risk", "flag_detail"]]
        merged = pd.read_csv(matrix_path)
        # 确保 mmsi 类型一致
        merged["mmsi"] = merged["mmsi"].astype(float).astype("Int64")
        flag_cols["mmsi"] = flag_cols["mmsi"].astype(float).astype("Int64")
        merged = merged.merge(flag_cols, on="mmsi", how="left")

        # 更新综合风险
        # sanction_sources (已有的) + flag_score 合成 final_risk
        if "sanction_sources" in merged.columns:
            merged["final_risk"] = merged.apply(
                lambda row: "极高风险" if row.get("sanction_sources", 0) >= 3 or row.get("flag_score", 0) >= 3
                else ("高风险" if row.get("sanction_sources", 0) >= 2 or row.get("flag_score", 0) >= 2
                else ("中风险" if row.get("sanction_sources", 0) >= 1 or row.get("flag_score", 0) >= 1
                else "低风险")),
                axis=1
            )

        merged_path = OUTPUT / "sanctions_matrix.csv"
        merged.to_csv(merged_path, index=False, encoding="utf-8-sig")
        print(f"[更新] 制裁矩阵已更新: {merged_path}")
        print(f"  最终风险分布:")
        for level in ["极高风险", "高风险", "中风险", "低风险"]:
            cnt = (merged["final_risk"] == level).sum()
            print(f"    {level}: {cnt} ({cnt/len(merged)*100:.1f}%)")

    print("\n完成")


if __name__ == "__main__":
    main()
