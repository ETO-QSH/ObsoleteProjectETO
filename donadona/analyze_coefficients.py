#!/usr/bin/env python3
"""
分析 `combinations_pass.csv`，统计每个词条出现次数，生成系数表（对数逆频率权重）。

脚本会：
 - 读取 `combinations_pass.csv`（自动在工作目录查找）
 - 统计 A/B/C 三列中每个词条的出现次数
 - 计算词条权重：weight_term = 1/ln(count)
   * count=1 时：ln(1)=0，权重为 0（被剔除）
   * count>1 时：weight = 1/ln(count)
 - 将系数保存为 `coefficients.csv`（包含：词条、原始计数、词条权重）

用法: python analyze_coefficients.py
"""

import csv
from collections import Counter
from pathlib import Path
import math


def find_pass_csv(dirp: Path) -> Path:
    for p in dirp.glob('*.csv'):
        name = p.name
        if 'combinations_pass' in name:
            return p
    raise FileNotFoundError('未找到 combinations_pass.csv，请将文件放到同一目录')


def load_rows(path: Path):
    with path.open('r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return reader.fieldnames or [], rows


def analyze_counts(rows):
    """统计 A/B/C 三列中每个词条的出现次数"""
    cnt = Counter()
    for r in rows:
        keys = list(r.keys())
        if len(keys) < 3:
            continue
        a = r.get(keys[0], '').strip()
        b = r.get(keys[1], '').strip()
        c = r.get(keys[2], '').strip()
        for name in (a, b, c):
            if name:
                cnt[name] += 1
    return cnt


def compute_term_weights(counter: Counter):
    """
    计算词条权重：weight = 1/ln(count)
    
    - count=1 时：ln(1)=0，权重为0（被自动剔除）
    - count>1 时：ln(count)>0，权重 = 1/ln(count)
    
    这样可以剔除低频词条并优化分布。
    """
    weights = {}
    for k, v in counter.items():
        if v <= 1:
            # 数量为1的词条权重设为0，会被剔除
            weights[k] = 0.0
        else:
            ln_v = math.log(v)
            weights[k] = 1.0 / ln_v if ln_v > 0 else 0.0
    return weights


def save_coefficients(path: Path, counter: Counter, weights: dict):
    """保存系数表：词条、原始计数、词条权重"""
    with path.open('w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['term', 'count', 'term_weight'])
        for term, cnt in counter.most_common():
            w.writerow([term, cnt, weights.get(term, 0)])


def compute_row_weights(rows, term_weights):
    """计算每行的最终抽取权重并返回权重列表。

    逻辑：inverse_weight = prod(term_weight for each term)
           row_weight = 1 / inverse_weight (若 inverse_weight>0)
    返回与 rows 对应的权重列表（float）。
    """
    row_weights = []
    for r in rows:
        keys = list(r.keys())
        if len(keys) < 3:
            row_weights.append(0.0)
            continue
        names = [r.get(keys[i], '').strip() for i in range(3)]
        prod = 1.0
        zero_flag = False
        for n in names:
            w = term_weights.get(n, 0.0)
            if w <= 0:
                zero_flag = True
                break
            prod *= w
        # row_weight defined as product of the three term weights
        if zero_flag or prod == 0:
            row_weights.append(0.0)
        else:
            row_weights.append(prod)
    return row_weights


def save_row_weights(path: Path, rows, fieldnames, row_weights):
    """保存条目权重表（仅保存权重>0的行）。列为原有字段加 `row_weight`。"""
    with path.open('w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(fieldnames + ['row_weight'])
        for r, rw in zip(rows, row_weights):
            if rw > 0:
                row_list = [r.get(fn, '') for fn in fieldnames]
                w.writerow(row_list + [rw])


def main():
    workdir = Path(__file__).parent
    try:
        csvp = find_pass_csv(workdir)
    except FileNotFoundError as e:
        print(e)
        return

    print('找到组合表:', csvp)
    fieldnames, rows = load_rows(csvp)
    print('表头字段数:', len(fieldnames))
    print('总行数:', len(rows))

    # 分析词条频率
    counter = analyze_counts(rows)
    print('共计不同词条:', len(counter))

    # 计算词条权重
    weights = compute_term_weights(counter)
    
    # 保存系数表
    coeff_path = workdir / 'coefficients.csv'
    save_coefficients(coeff_path, counter, weights)
    print('已保存系数表:', coeff_path)
    
    # 打印前20个词条的频率和权重
    print('\n词条频率和权重（前20个）：')
    for term, cnt in counter.most_common(20):
        w = weights.get(term, 0)
        print(f'  {term}: count={cnt}, term_weight={w:.6f}')

    # 计算并保存每一行的条目权重（只保存权重>0的条目）
    try:
        combos_path = find_pass_csv(workdir)
        _, rows = load_rows(combos_path)
        row_weights = compute_row_weights(rows, weights)
        row_weights_path = workdir / 'row_weights.csv'
        # 使用原组合表头保存
        fieldnames, _ = load_rows(combos_path)
        save_row_weights(row_weights_path, rows, fieldnames, row_weights)
        non_zero = sum(1 for v in row_weights if v > 0)
        print(f'已保存条目权重表（非零条目数: {non_zero}）:', row_weights_path)
    except Exception as e:
        print('生成条目权重失败:', e)


if __name__ == '__main__':
    main()
