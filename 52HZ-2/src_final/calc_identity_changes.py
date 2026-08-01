"""
脚本4: 身份变更频率指标（预留）
================================
预期输入: 决赛资料/身份变更记录.csv
  列: mmsi, change_date, change_field (name/flag/owner/imo), old_value, new_value
输出: output_final/identity_changes.csv
  列: mmsi, name_changes, flag_changes, owner_changes, total_identity_changes, last_change_date

目前赛方数据尚未提供，脚本框架已就绪。
"""

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).parent.parent
INPUT_PATH = ROOT / "决赛资料" / "身份变更记录.csv"
OUTPUT_PATH = ROOT / "output_final" / "identity_changes.csv"


def process(input_path: Path) -> pd.DataFrame:
    """处理身份变更记录，计算每艘船的变更次数"""
    df = pd.read_csv(input_path)

    # ---- 根据实际列名调整 ----
    # 预期列名映射（赛方实际列名可能不同）
    col_map = {
        "mmsi": "mmsi",
        "change_field": "change_field",   # name / flag / owner / imo
        "old_value": "old_value",
        "new_value": "new_value",
    }

    # 尝试自动适配列名
    actual_cols = list(df.columns)
    print(f"[身份变更] 实际列名: {actual_cols}")

    # 找到 MMSI 列
    mmsi_col = None
    for c in actual_cols:
        if "mmsi" in c.lower():
            mmsi_col = c
            break
    if not mmsi_col:
        mmsi_col = actual_cols[0]

    # 找到变更字段列
    field_col = None
    for c in actual_cols:
        if any(kw in c.lower() for kw in ["field", "type", "字段", "类型", "变更"]):
            field_col = c
            break

    # ---- 按 MMSI 统计变更次数 ----
    df[mmsi_col] = pd.to_numeric(df[mmsi_col], errors="coerce").astype("Int64")
    df = df.dropna(subset=[mmsi_col])

    result_rows = {}
    for mmsi, group in df.groupby(mmsi_col):
        m = int(mmsi)
        row = {"mmsi": m, "name_changes": 0, "flag_changes": 0,
               "owner_changes": 0, "total_identity_changes": len(group)}

        if field_col:
            for _, r in group.iterrows():
                val = str(r[field_col]).lower()
                if "name" in val or "船名" in val:
                    row["name_changes"] += 1
                elif "flag" in val or "船旗" in val or "flag_state" in val:
                    row["flag_changes"] += 1
                elif "owner" in val or "船东" in val or "operator" in val:
                    row["owner_changes"] += 1
        else:
            # 没有变更类型列，全部算总数
            pass

        row["last_change_date"] = str(group.iloc[-1].get("change_date", ""))
        result_rows[m] = row

    result = pd.DataFrame(list(result_rows.values()))
    result = result[["mmsi", "name_changes", "flag_changes", "owner_changes",
                     "total_identity_changes", "last_change_date"]]
    result = result.sort_values("total_identity_changes", ascending=False)
    return result


if __name__ == "__main__":
    print("=" * 60)
    print("身份变更频率指标")
    print("=" * 60)

    if INPUT_PATH.exists():
        print(f"[处理] {INPUT_PATH}")
        df = process(INPUT_PATH)
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
        print(f"[输出] {OUTPUT_PATH}")
        print(f"  船只: {len(df)}")
        print(f"  有变更: {(df['total_identity_changes'] > 0).sum()}")
        print(f"  最大变更次数: {df['total_identity_changes'].max()}")
    else:
        print(f"\n[等待] 数据文件尚未提供: {INPUT_PATH}")
        print(f"  预期格式: CSV，包含 mmsi, change_date, change_field 列")
        print(f"  数据到后直接运行本脚本即可")
