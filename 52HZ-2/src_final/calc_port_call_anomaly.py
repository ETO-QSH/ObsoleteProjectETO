"""
脚本5: 靠泊记录异常指标（预留）
================================
预期输入: 决赛资料/原油港口靠泊记录.csv
  列: mmsi, port_name, terminal, arrival_time, departure_time
辅助:   ais_clean_2026.parquet + 原油装卸港清单_详细.csv
输出:   output_final/port_call_anomaly.csv
  列: mmsi, recorded_calls, ais_estimated_calls, unrecorded_call_ratio

逻辑:
  1. 从靠泊记录统计每艘船在原油港口的靠泊次数 → recorded_calls
  2. 从 AIS 轨迹检测每艘船在港口25km内低速停留 → ais_estimated_calls
  3. AIS有但记录无 → 隐蔽靠泊 → unrecorded_call_ratio

目前赛方数据尚未提供，脚本框架已就绪。
"""

import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).parent.parent
INPUT_PATH = ROOT / "决赛资料" / "原油港口靠泊记录.csv"
PORTS_CSV = ROOT / "决赛资料" / "原油装卸港清单" / "原油装卸港清单_详细.csv"
PARQUET_CLEAN = ROOT / "database" / "ais_clean_2026.parquet"
OUTPUT_PATH = ROOT / "output_final" / "port_call_anomaly.csv"


def process(input_path: Path) -> pd.DataFrame:
    """处理靠泊记录，比对 AIS 轨迹"""
    # ---- 1. 加载靠泊记录 ----
    records = pd.read_csv(input_path)
    print(f"[靠泊] 记录数: {len(records)}")
    print(f"  列名: {list(records.columns)}")

    # 尝试找到 MMSI 列
    mmsi_col = None
    for c in records.columns:
        if "mmsi" in c.lower():
            mmsi_col = c
            break
    if not mmsi_col:
        mmsi_col = records.columns[0]

    records[mmsi_col] = pd.to_numeric(records[mmsi_col], errors="coerce").astype("Int64")

    # ---- 2. 统计每艘船的记录靠泊次数 ----
    recorded = records.groupby(mmsi_col).size().reset_index(name="recorded_calls")
    recorded.columns = ["mmsi", "recorded_calls"]

    # ---- 3. 从 AIS 检测靠泊事件（预留） ----
    # 思路：读取 ais_clean，对每艘船检测在港口 25km 内低速（<1节）持续 >2h 的事件
    # 这里留空框架，数据到后填充

    # ---- 4. 合并比对 ----
    # 目前只输出 recorded_calls，ais_estimated_calls 和 unrecorded_call_ratio 留空
    result = recorded.copy()
    result["ais_estimated_calls"] = 0  # TODO: AIS 靠泊检测
    result["unrecorded_call_ratio"] = 0.0  # TODO: (ais - recorded) / ais

    result["mmsi"] = result["mmsi"].astype("Int64")
    return result


if __name__ == "__main__":
    print("=" * 60)
    print("靠泊记录异常指标")
    print("=" * 60)

    if INPUT_PATH.exists():
        print(f"[处理] {INPUT_PATH}")
        df = process(INPUT_PATH)
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
        print(f"[输出] {OUTPUT_PATH}")
        print(f"  船只: {len(df)}")
    else:
        print(f"\n[等待] 数据文件尚未提供: {INPUT_PATH}")
        print(f"  预期格式: CSV，包含 mmsi, port_name, arrival_time, departure_time")
        print(f"  数据到后完善 AIS 靠泊检测逻辑即可")
