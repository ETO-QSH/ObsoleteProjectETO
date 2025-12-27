import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

plt.rcParams['font.sans-serif'] = ['Lolita']
DIR = r"D:\Desktop\Desktop\52HZ\1、原油贸易、成品油贸易数据"
files = {
    "crude": os.path.join(DIR, "中国进口原油海运量_2025-10-17.xls"),
    "pgi": os.path.join(DIR, "中国进口成品油海运量_2025-10-17.xls"),
    "pge": os.path.join(DIR, "中国出口成品油海运量_2025-10-17.xls"),
}


def read_idx(fn, col_idx=2, col_name=None):
    df = pd.read_excel(fn, skiprows=1, usecols=[0, col_idx])
    df.columns = ["Date", col_name or "Value"]
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.drop_duplicates(subset=["Date"])
    return df.set_index("Date")


crude = read_idx(files["crude"], col_name="Crude_Imp")
pgi = read_idx(files["pgi"], col_name="PG_Imp")
pge = read_idx(files["pge"], col_name="PG_Exp")

df = pd.concat([crude, pgi, pge], axis=1).loc["2015-09":"2025-08"]
df["PG_NetImp"] = df["PG_Imp"] - df["PG_Exp"]
df["Total_Feed"] = df["Crude_Imp"] + df["PG_NetImp"]

print(df.head())
print(df["Total_Feed"].describe())

x = np.arange(len(df))
y = df["Total_Feed"].values
slope, intercept = np.polyfit(x, y, 1)
line = slope * x + intercept

initial_value = intercept
final_value = slope * (len(df) - 1) + intercept
years = len(df) / 12
mean_growth_rate = ((final_value - initial_value) / initial_value / years) * 100

print(f"Slope: {slope}, Intercept: {intercept}")

plt.figure(figsize=(6, 4))
plt.scatter(df.index, y, color='steelblue', label='月度产能 (10kt)', s=5)
plt.plot(df.index, line, color='crimson', linewidth=1, label=f'线性趋势 ({mean_growth_rate:.1f}%)')
plt.title("中国炼油产能变化 (2015-09 ~ 2025-08)")
plt.legend()
plt.show()

plt.savefig("China_Refinery.png", dpi=300)
df.to_csv("China_Refinery.csv", encoding="utf-8")
