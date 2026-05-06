#!/usr/bin/env python3
import csv
from pathlib import Path
from itertools import combinations
from typing import List, Tuple

CSV_DIR = Path(r"d:\Desktop\Desktop\donadona")
CSV_PATH = None
for p in CSV_DIR.glob('*.csv'):
    if 'ドーナドーナ' in p.name or 'ドーナ' in p.name:
        CSV_PATH = p
        break
if CSV_PATH is None:
    CSV_PATH = CSV_DIR / 'ドーナドーナ全62个詞条加成一览.csv'

OUT_CSV = CSV_DIR / 'combinations_pass.csv'

def to_int_safe(v: str) -> int:
    if v is None:
        return 0
    s = str(v).strip()
    if s == '':
        return 0
    try:
        return int(s)
    except Exception:
        s2 = s.replace('"', '').replace(',', '')
        try:
            return int(s2)
        except Exception:
            return 0

def load_attributes(path: Path) -> List[Tuple[str,int,int,int]]:
    if not path.exists():
        raise FileNotFoundError(f'CSV not found: {path}')
    items = []
    with path.open('r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        # Attempt to find keys; accept a few variants
        fieldnames = [n.strip() for n in reader.fieldnames or []]
        # normalized mapping
        key_map = {}
        for name in fieldnames:
            n = name.replace('\ufeff','')
            if n in ('属性','name'):
                key_map['name'] = name
            if n in ('外貌变动','外貌変動','AppearanceDelta'):
                key_map['a_delta'] = name
            if n in ('技巧变动','技巧変動','SkillDelta'):
                key_map['b_delta'] = name
            if n in ('精神变动','精神変動','MindDelta'):
                key_map['c_delta'] = name
        # Fallback to exact header names if not matched
        if 'name' not in key_map:
            for n in fieldnames:
                if '属' in n or '属性' in n or 'name' in n.lower():
                    key_map['name'] = n
        if 'a_delta' not in key_map:
            for n in fieldnames:
                if '外貌' in n and '变' in n or '変' in n:
                    key_map['a_delta'] = n
        if 'b_delta' not in key_map:
            for n in fieldnames:
                if '技巧' in n and ('变' in n or '変' in n):
                    key_map['b_delta'] = n
        if 'c_delta' not in key_map:
            for n in fieldnames:
                if '精神' in n and ('变' in n or '変' in n):
                    key_map['c_delta'] = n

        if not all(k in key_map for k in ('name','a_delta','b_delta','c_delta')):
            raise ValueError(f'无法识别必要列，现有表头: {fieldnames}')

        for row in reader:
            name = row.get(key_map['name'], '').strip()
            a = to_int_safe(row.get(key_map['a_delta']))
            b = to_int_safe(row.get(key_map['b_delta']))
            c = to_int_safe(row.get(key_map['c_delta']))
            items.append((name, a, b, c))
    return items

def main():
    try:
        items = load_attributes(CSV_PATH)
    except Exception as e:
        print('加载 CSV 出错:', e)
        return

    # filter out empty-name rows
    items = [it for it in items if it[0]]
    # exclude specific entries
    EXCLUDE = {'無想', '無垢', '無相'}
    before = len(items)
    items = [it for it in items if it[0] not in EXCLUDE]
    excluded = before - len(items)
    if excluded:
        print(f'已排除指定词条，数量: {excluded}')
    total = 0
    matches = []
    for a,b,c in combinations(items, 3):
        names = (a[0], b[0], c[0])
        sala = a[1] + b[1] + c[1]
        slb = a[2] + b[2] + c[2]
        slc = a[3] + b[3] + c[3]
        # condition: 外貌变动 >=200，技巧变动>=0，精神变动>=600
        if sala >= 200 and slb >= 0 and slc >= 600:
            matches.append((names, sala, slb, slc))
        total += 1

    print(f'共计算 {total} 个组合，符合条件的数量: {len(matches)}')
    if matches:
        # sort by total sum (外貌+技巧+精神), then 精神, 外貌, 技巧 — all desc
        matches.sort(key=lambda t: (t[1] + t[2] + t[3], t[3], t[1], t[2]), reverse=True)
        # write to CSV (sorted)
        with OUT_CSV.open('w', encoding='utf-8', newline='') as f:
            w = csv.writer(f)
            w.writerow(['A', 'B', 'C', '外貌', '技巧', '精神', '总和'])
            for names, sa, sb, sc in matches:
                total_sum = sa + sb + sc
                w.writerow([names[0], names[1], names[2], sa, sb, sc, total_sum])

        # print first 50 to console
        for i, (names, sa, sb, sc) in enumerate(matches[:50], start=1):
            print(i, names, '外貌=', sa, '技巧=', sb, '精神=', sc, '总和=', sa + sb + sc)
        if len(matches) > 50:
            print('... (only first 50 printed)')
        print('已将全部符合组合（排序后）写入:', OUT_CSV)

if __name__ == '__main__':
    main()
