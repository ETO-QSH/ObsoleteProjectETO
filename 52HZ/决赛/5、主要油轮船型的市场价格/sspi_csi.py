import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

plt.rcParams['font.sans-serif'] = ['Lolita']
DIR = r"D:\Desktop\Desktop\52HZ\5、主要油轮船型的市场价格"

second_path = os.path.join(DIR, "二手油船价格指数_2025-10-17.xls")
new_path = os.path.join(DIR, "新油船价格指数_2025-10-17.xls")

start_date = "2015-09-01"
end_date = "2025-08-31"


def read_and_clip(path, col_name):
    df = pd.read_excel(path, usecols=[0, 1], names=["日期", col_name])
    df["日期"] = pd.to_datetime(df["日期"])
    return df.set_index("日期").sort_index().loc[start_date:end_date]


df_second = read_and_clip(second_path, "二手指数")
df_new = read_and_clip(new_path, "新指数")
df_merge = pd.concat([df_second, df_new], axis=1, join='inner')


def fit_trend(sr):
    x = np.arange(len(sr))
    slope, inter = np.polyfit(x, sr.values, 1)
    line = slope * x + inter
    growth = ((line[-1] - line[0]) / line[0] / (len(line) - 1) * 12 * 100)
    return line, growth


trend_second, g_second = fit_trend(df_merge["二手指数"])
trend_new, g_new = fit_trend(df_merge["新指数"])

plt.figure(figsize=(6, 4))
plt.plot(df_merge.index, df_merge["二手指数"], color='tab:blue', lw=1, label='二手油船价格指数')
plt.plot(df_merge.index, df_merge["新指数"], color='tab:orange', lw=1, label='新油船价格指数')
plt.plot(df_merge.index, trend_second, color='blue', ls='--', lw=1, label=f'二手趋势 ({g_second:.1f}%)')
plt.plot(df_merge.index, trend_new, color='orange', ls='--', lw=1, label=f'新船趋势 ({g_new:.1f}%)')

plt.title("油船价格指数对比 (2015-09 ~ 2025-08)")
plt.legend()
plt.show()

plt.savefig("Tanker_Price_Index_Compare.png", dpi=300)
df_merge.to_csv("Tanker_Price_Index_Monthly.csv", encoding="utf-8")
