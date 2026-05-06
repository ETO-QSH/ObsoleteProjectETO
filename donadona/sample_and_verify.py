import csv
import random
from collections import Counter
from pathlib import Path


def sampling(row_weights_path, samples=1, output=False):
    with open(row_weights_path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    weight_idx = len(header) - 1
    term_idxs = [0, 1, 2]

    sampling_weights = []
    for r in rows:
        v = float(r[weight_idx])
        sampling_weights.append(v if v > 0 else 0.0)

    sampled = random.choices(list(range(len(rows))), weights=sampling_weights, k=samples)

    cnt = Counter()
    for i in sampled:
        row = rows[i]
        for ti in term_idxs:
            if ti < len(row):
                name = row[ti].strip()
                if name:
                    cnt[name] += 1

    if output:
        with open('sample_counts.csv', 'w', encoding='utf-8', newline='') as f:
            w = csv.writer(f)
            w.writerow(['term', 'sample_count'])
            for term, c in cnt.most_common():
                w.writerow([term, c])

    return cnt


if __name__ == '__main__':
    cnt = sampling('row_weights.csv', 10000, True)
    for term, c in cnt.most_common():
        print(f'{term}: {c}')
