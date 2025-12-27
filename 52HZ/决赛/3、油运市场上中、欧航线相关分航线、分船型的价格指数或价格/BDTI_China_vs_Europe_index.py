import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

plt.rcParams['font.sans-serif'] = ['Lolita']
DIR = r"D:\Desktop\Desktop\52HZ\3、油运市场上中、欧航线相关分航线、分船型的价格指数或价格"
file_path = os.path.join(DIR, "BDTI分航线运价指数（日）_2025-10-17.xls")

START = "2022-09-01"
END = "2025-08-31"
STEP = 12

TONS = {
    "TD3C": 270_000,
    "TD15": 260_000,
    "TD7": 80_000,
    "TD6": 135_000,
}

CHINA_T = TONS["TD3C"] + TONS["TD15"]
EUROPE_T = TONS["TD7"] + TONS["TD6"]
W_CHINA = TONS["TD3C"] / CHINA_T
W_EUROPE = TONS["TD7"] / EUROPE_T

df = (pd.read_excel(file_path, usecols=[0, 1, 2], names=["日期", "航线", "BDTI"])
        .assign(日期=lambda x: pd.to_datetime(x["日期"])).set_index("日期").sort_index()).loc[START:END]


monthly = {}
for route in df["航线"].unique():
    ser = (df[df["航线"] == route].loc[:, "BDTI"].resample("MS").mean().dropna())
    ser.index = ser.index.strftime("%Y-%m")
    monthly[route] = ser

big = pd.concat(monthly, axis=1)
big.columns = list(big.columns)

china_cols = [c for c in big.columns if c in ("TD3C", "TD15")]
europe_cols = [c for c in big.columns if c in ("TD7", "TD6")]

big["中国加权"] = (big[china_cols].mul([W_CHINA, 1 - W_CHINA], axis=1).sum(axis=1) if len(china_cols) == 2 else big[china_cols[0]])
big["欧洲加权"] = (big[europe_cols].mul([W_EUROPE, 1 - W_EUROPE], axis=1).sum(axis=1) if len(europe_cols) == 2 else big[europe_cols[0]])

x = np.arange(len(big))
for col in ["中国加权", "欧洲加权"]:
    slope, intercept = np.polyfit(x, big[col], 1)
    big[f"{col} 线性"] = slope * x + intercept

plt.figure(figsize=(6, 4))
for col in big.columns[:-4]:
    plt.plot(big.index, big[col], label=f"{col} 月平均", linewidth=1)

label_sparse = [lab.split("-")[0] for lab in big.index[::12]]
plt.xticks(np.arange(len(big))[::12], label_sparse, rotation=0)
plt.title("BDTI 分航线指数 (2022-09 ~ 2025-08) - 全航线")
plt.legend()
plt.show()

plt.figure(figsize=(6, 4))
plt.plot(big.index, big["中国加权"], label="中国加权 (TD3C+TD15)", linewidth=1)
plt.plot(big.index, big["欧洲加权"], label="欧洲加权 (TD7+TD6)", linewidth=1)

for col in ["中国加权 线性", "欧洲加权 线性"]:
    rate = (big[col].iloc[-1] - big[col].iloc[0]) / big[col].iloc[0] / (len(big) / 12)
    plt.plot(big.index, big[col], "--", label=f"{col[:2]}线性趋势 ({rate:.1%})", linewidth=1)

plt.xticks(np.arange(len(big))[::12], label_sparse, rotation=0)
plt.title("BDTI 航线加权 (2022-09 ~ 2025-08)")
plt.legend()
plt.show()

# plt.savefig("BDTI_AllRoutes.png", dpi=300)
# plt.savefig("BDTI_CN_vs_EU_Routes.png", dpi=300)
big.to_csv("BDTI_AllRoutes_Weighted.csv", encoding="utf-8", index_label="日期")
