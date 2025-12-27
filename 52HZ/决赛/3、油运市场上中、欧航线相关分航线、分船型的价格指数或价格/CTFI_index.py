import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

plt.rcParams['font.sans-serif'] = ['Lolita']
DIR = r"D:\Desktop\Desktop\52HZ\3、油运市场上中、欧航线相关分航线、分船型的价格指数或价格"
file_path = os.path.join(DIR, "中国进口原油运价指数_2025-10-17.xls")


def read_data(file_path):
    df = pd.read_excel(file_path, usecols=[0, 1, 4])
    df.columns = ["日期", "航线", "价格指数"]
    df["日期"] = pd.to_datetime(df["日期"])
    return df.sort_values("日期").set_index("日期")


df = read_data(file_path)
df = df.loc["2020-09-01": "2025-08-31"]

monthly = {}
routes = df["航线"].unique()
for route in routes:
    ser = (df[df["航线"] == route].loc[:, "价格指数"].resample("MS").mean())
    ser.index = ser.index.strftime("%Y-%m")
    monthly[route] = ser

big = pd.concat(monthly, axis=1)
big.columns = list(big.columns)

x_pos = np.arange(len(big))
x_lab = big.index
step = 12

WEIGHT1, WEIGHT2 = 26 / (26 + 27), 27 / (26 + 27)
big["加权平均"] = (big.iloc[:, 0] * WEIGHT1 + big.iloc[:, 1] * WEIGHT2)

x = np.arange(len(big))
slope, intercept = np.polyfit(x, big["加权平均"], 1)
big["线性拟合"] = slope * x + intercept

initial_value = intercept
final_value = slope * (len(big) - 1) + intercept
years = len(big) / 12
mean_growth_rate = ((final_value - initial_value) / initial_value / years) * 100

plt.figure(figsize=(6, 4))
for col in big.columns[:-2]:
    plt.plot(big.index, big[col], label=f"{col[:2]}-宁波 月平均", linewidth=1)

plt.plot(big.index, big["加权平均"], label="加权平均 (载货量)", linewidth=1)
plt.plot(big.index, big["线性拟合"], color="crimson", label=f"线性趋势 ({mean_growth_rate:.1f}%)")

label_sparse = [lab.split("-")[0] for lab in x_lab[::step]]
plt.xticks(x_pos[4::step], label_sparse, rotation=0)
plt.title("中国进口原油运价指数 (2020-09 ~ 2025-08)")
plt.legend()
plt.show()

plt.savefig("CTFI_Monthly_Avg.png", dpi=300)
big.to_csv("CTFI_Monthly_Avg.csv", encoding="utf-8", index_label="日期")
