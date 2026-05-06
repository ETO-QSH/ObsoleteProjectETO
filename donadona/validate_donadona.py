#!/usr/bin/env python3
import csv
from pathlib import Path
from typing import List, Tuple

CSV_PATH = Path(r"d:\Desktop\Desktop\donadona\ドーナドーナ全62个詞条加成一览.csv")
CSV_PATH2 = Path(r"d:\Desktop\Desktop\donadona\ドーナドーナ全62个詞条加成一覧.csv")
# Prefer existing file; fall back to the other common name
if not CSV_PATH.exists():
    for p in Path(r"d:\Desktop\Desktop\donadona").glob('*.csv'):
        if 'ドーナドーナ' in p.name:
            CSV_PATH = p
            break

NUM_COLS = [
    '外貌', '技巧', '精神',
    '外貌变动', '技巧变动', '精神变动',
    '基础总和', '变动总和'
]

def to_int(s: str) -> Tuple[int, bool]:
    """Convert string to int. Returns (value, was_empty).
    Empty or whitespace-only strings return (0, True).
    Non-numeric strings raise ValueError.
    """
    if s is None:
        return 0, True
    s2 = s.strip()
    if s2 == '':
        return 0, True
    try:
        return int(s2), False
    except ValueError:
        # Try to remove quotes or other stray characters then int
        s3 = s2.replace('"', '').replace(',', '')
        return int(s3), False


def main():
    if not CSV_PATH.exists():
        print('CSV file not found in expected location:', CSV_PATH)
        return

    with CSV_PATH.open('r', encoding='utf-8', newline='') as f:
        reader = list(csv.reader(f))
    if not reader:
        print('Empty CSV')
        return
    header = reader[0]
    # map header names to indices
    idx = {name: i for i, name in enumerate(header)}
    # required columns check
    required = ['属性'] + NUM_COLS
    for col in NUM_COLS:
        if col not in idx:
            print(f'缺少列: {col}，请确认 CSV 表头是否为中文字段名。当前表头:', header)
            return

    mismatches: List[Tuple[int, str]] = []
    parsed_rows = []
    for i, row in enumerate(reader[1:], start=2):
        # ensure row has enough columns
        if len(row) < len(header):
            # pad
            row = row + [''] * (len(header) - len(row))
        try:
            a, ae = to_int(row[idx['外貌']])
            b, be = to_int(row[idx['技巧']])
            c, ce = to_int(row[idx['精神']])
            ca, cae = to_int(row[idx['外貌变动']])
            cb, cbe = to_int(row[idx['技巧变动']])
            cc, cce = to_int(row[idx['精神变动']])
            base_field, base_empty = to_int(row[idx['基础总和']])
            change_field, change_empty = to_int(row[idx['变动总和']])
        except Exception as e:
            mismatches.append((i, f'解析错误: {e}'))
            parsed_rows.append((row, {}))
            continue

        base_calc = a + b + c
        change_calc = ca + cb + cc

        detail = {}
        if base_calc != base_field:
            detail['基础差异'] = (base_calc, base_field)
        if change_calc != change_field:
            detail['变动差异'] = (change_calc, change_field)

        if detail:
            mismatches.append((i, detail))

        parsed_rows.append((row, {
            'a': (a, ae), 'b': (b, be), 'c': (c, ce),
            'ca': (ca, cae), 'cb': (cb, cbe), 'cc': (cc, cce),
            'base_field': (base_field, base_empty), 'change_field': (change_field, change_empty)
        }))

    if mismatches:
        print('发现不匹配行:')
        for ln, info in mismatches:
            print('-', ln, info)
        print('\n请手动检查上述行的数值或表头。空字符串在计算时视为0。')
        return

    # all passed: fill empty numeric positions with 0 and write back
    out_rows = [header]
    for row, parsed in parsed_rows:
        new_row = list(row)
        # fill numeric columns if empty
        for col in NUM_COLS:
            j = idx[col]
            # extend row if needed
            if j >= len(new_row):
                new_row += [''] * (j - len(new_row) + 1)
            if new_row[j].strip() == '':
                new_row[j] = '0'
        out_rows.append(new_row)

    backup = CSV_PATH.with_suffix('.bak.csv')
    CSV_PATH.replace(backup)
    with CSV_PATH.open('w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(out_rows)

    print('全部通过。已将空值填为0，原文件备份为:', str(backup))


if __name__ == '__main__':
    main()
