import csv
import pathlib
from bs4 import BeautifulSoup


INPUT, OUTPUT = 'raw_html_div.txt', 'Shanghai Schedule.csv'
rows = [['Carrier', 'Name', 'Voyage', 'ETA', 'ETB', 'ETD']]
soup = BeautifulSoup(pathlib.Path('raw_html_div.txt').read_text(encoding='utf-8'), 'lxml')

for block in soup.select('.pYplGY'):
    carrier = block.select_one('.IUKudo').get_text(strip=True)
    for row in block.select('.u3xCoJ'):
        rows.append([carrier, *[s.get_text(strip=True) for s in row.select('.rVqe2J')[:5]]])

with open(OUTPUT, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerows(rows)

print(f'已生成 {len(rows)} 条记录 -> {OUTPUT}')
