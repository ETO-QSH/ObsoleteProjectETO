import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os


plt.rcParams['font.sans-serif'] = ['Lolita']
DIR = r"D:\Desktop\Desktop\52HZ\3、油运市场上中、欧航线相关分航线、分船型的价格指数或价格"
file_path = os.path.join(DIR, "BDTI_2025-10-17.xls")


def read_data(file_path):
    df = pd.read_excel(file_path, usecols=[0, 1])
    df.columns = ["日期", "BDTI"]
    df["日期"] = pd.to_datetime(df["日期"])
    df = df.set_index("日期")
    return df.sort_index()


start_date = "2015-09-01"
end_date = "2025-08-31"

df = read_data(file_path)
df = df.loc[start_date:end_date]

monthly_avg = df.resample('MS').mean()

x = np.arange(len(df))
y = df["BDTI"].values
slope, intercept = np.polyfit(x, y, 1)
line = slope * x + intercept

initial_value = intercept
final_value = slope * (len(df) - 1) + intercept
mean_growth_rate = ((final_value - initial_value) / initial_value / 10) * 100

# 打印年均增长率
print(f"Initial Value: {initial_value}, Final Value: {final_value}, Mean Annual Growth Rate: {mean_growth_rate:.2f}%")

# 绘制图形
plt.figure(figsize=(6, 4))
plt.plot(monthly_avg.index, monthly_avg, color='blue', linewidth=1, label='BDTI (Point)')
plt.plot(df.index, line, color='crimson', linewidth=1, label=f'线性趋势 ({mean_growth_rate:.1f}%)')
plt.title("BDTI 变化趋势 (2015-09 ~ 2025-08)")
plt.legend()
plt.show()

plt.savefig("BDTI_Monthly_Avg.png", dpi=300)
monthly_avg.to_csv("BDTI_Monthly_Avg.csv", encoding="utf-8")
