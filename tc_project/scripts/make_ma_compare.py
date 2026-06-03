import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

base = Path('.')
input_path = base / 'data' / 'processed' / 'merged_data.csv'
out_path = base / 'report' / 'figures' / 'ma_compare.png'
out_path.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(input_path, usecols=['时间', '收盘价'])
df['时间'] = pd.to_datetime(df['时间'], errors='coerce')
df['收盘价'] = pd.to_numeric(df['收盘价'], errors='coerce')
df = df.sort_values('时间').dropna(subset=['时间', '收盘价']).reset_index(drop=True)

for window in [5, 10, 20, 60]:
    df[f'MA{window}'] = df['收盘价'].rolling(window=window, min_periods=1).mean()

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(df['时间'], df['收盘价'], color='#444444', linewidth=0.7, alpha=0.55, label='收盘价')
ax.plot(df['时间'], df['MA5'], color='#d62728', linewidth=1.5, label='MA5')
ax.plot(df['时间'], df['MA10'], color='#ff7f0e', linewidth=1.5, label='MA10')
ax.plot(df['时间'], df['MA20'], color='#2ca02c', linewidth=1.5, label='MA20')
ax.plot(df['时间'], df['MA60'], color='#1f77b4', linewidth=1.8, label='MA60')
ax.set_title('不同周期移动平均线')
ax.set_xlabel('时间')
ax.set_ylabel('价格')
ax.legend(ncol=5, frameon=False, loc='upper left')
fig.autofmt_xdate()
plt.tight_layout()
fig.savefig(out_path, dpi=300, bbox_inches='tight')
plt.close(fig)
print(out_path)
