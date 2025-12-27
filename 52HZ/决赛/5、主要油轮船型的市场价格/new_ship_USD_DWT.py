import pandas as pd
import matplotlib.pyplot as plt
import os

plt.rcParams['font.sans-serif'] = ['Lolita']
DIR = r"D:\Desktop\Desktop\52HZ\5、主要油轮船型的市场价格"
FILE = os.path.join(DIR, "新船价格_2025-10-17.xls")

DWT_MAP = {
    '灵便型': 32000,
    '巴拿马型': 75000,
    '阿芙拉型': 110000,
    '苏伊士型': 160000,
    'VLCC': 300000
}

df = pd.read_excel(FILE, usecols=[0, 1, 2], names=['年月', '船型', '价格'])
df['年月'] = pd.to_datetime(df['年月'])
df = df.set_index('年月').sort_index()
df = df.loc['2015-09':'2025-08'].copy()

df['单位价格'] = df.apply(lambda row: row['价格'] * 1e6 / DWT_MAP[row['船型']], axis=1)

plt.figure(figsize=(6, 4))
for ship in df['船型'].unique():
    sub = df[df['船型'] == ship]
    plt.plot(sub.index, sub['价格'], label=ship)

plt.title('新船价格走势 (2015-09 ~ 2025-08)')
plt.legend()
plt.show()

plt.figure(figsize=(6, 4))
for ship in df['船型'].unique():
    sub = df[df['船型'] == ship]
    plt.plot(sub.index, sub['单位价格'], label=ship)

plt.title('新船单位载重价格走势 (2015-09 ~ 2025-08)')
plt.legend()
plt.show()

# plt.savefig('Newbuilding_Price_by_Type.png', dpi=300)
# plt.savefig('Newbuilding_UnitPrice_by_Type.png', dpi=300)
df.to_csv('Newbuilding_Price_and_UnitPrice.csv', encoding='utf-8')
