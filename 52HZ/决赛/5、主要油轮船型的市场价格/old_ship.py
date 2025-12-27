import pandas as pd
import matplotlib.pyplot as plt
import os

plt.rcParams['font.sans-serif'] = ['Lolita']
DIR = r"D:\Desktop\Desktop\52HZ\5、主要油轮船型的市场价格"

f_new = os.path.join(DIR, "新船价格_2025-10-17.xls")
f_sec = os.path.join(DIR, "二手船价格_2025-10-17.xls")

out_png = os.path.join(DIR, 'Ship_Depreciation_Rate_Trends.png')
out_csv = os.path.join(DIR, 'Ship_Depreciation_Rate_Monthly.csv')

start_date = "2015-09"
end_date = "2025-08"


def read_new(path):
    df = pd.read_excel(path, skiprows=1, usecols=[0, 1, 2], names=['年月', '船型', '价格'])
    df['年月'] = pd.to_datetime(df['年月'], errors='coerce')
    df = df.dropna(subset=['年月'])
    return df.set_index('年月').sort_index().loc[start_date:end_date]


def read_sec(path):
    df = pd.read_excel(path, skiprows=1, usecols=[0, 1, 2, 3], names=['年月', '船型', '船龄', '价格'])
    df['船龄'] = df['船龄'].astype(str).str.replace('年', '', regex=False).astype(int)
    df['年月'] = pd.to_datetime(df['年月'], errors='coerce')
    df = df.dropna(subset=['年月'])
    return df.set_index('年月').sort_index().loc[start_date:end_date]


df_new = read_new(f_new)
df_sec = read_sec(f_sec)
data = {}

for ym, ship, price in zip(df_new.index, df_new['船型'], df_new['价格']):
    ym = ym.to_period('M')
    data.setdefault(ym, {}).setdefault(ship, {})[0] = price

for ym, ship, age, price in zip(df_sec.index, df_sec['船型'], df_sec['船龄'], df_sec['价格']):
    ym = ym.to_period('M')
    data.setdefault(ym, {}).setdefault(ship, {})[age] = price

records = []
for ym in sorted(data):
    for ship in data[ym]:
        if 0 not in data[ym][ship]:
            continue
        new_price = data[ym][ship][0]
        for age in [5, 10, 15]:
            if age not in data[ym][ship]:
                continue
            old_price = data[ym][ship][age]
            rate = 1 - old_price / new_price
            records.append({'年月': ym.to_timestamp(), '船型': ship, '船龄': age, '折旧率': rate})

df_rate = pd.DataFrame(records)
avg_rate = df_rate.groupby(['船型', '船龄'])['折旧率'].mean()
for (ship, age), val in avg_rate.items():
    print(f"{ship}_{age}年: {val:.2%}")

fig, axes = plt.subplots(2, 2, figsize=(14, 8), sharex=True)
axes = axes.flatten()
ship_list = ['阿芙拉型', '苏伊士型', 'VLCC', '巴拿马型']

for ax, ship in zip(axes, ship_list):
    sub = df_rate[df_rate['船型'] == ship]

    for age in [5, 10, 15]:
        tmp = sub[sub['船龄'] == age]
        if not tmp.empty:
            ax.plot(tmp['年月'], tmp['折旧率'], marker='o', ms=3, label=f'{age}年')

    ax.set_title(f'{ship} 折旧率变化')
    ax.grid(alpha=0.3)
    ax.legend()

fig.suptitle('二手油船折旧率 (2015-09 ~ 2025-08)')
plt.savefig(out_png, dpi=300)
plt.show()

df_rate.to_csv(out_csv, index=False, encoding='utf-8-sig', float_format='%.4f')
