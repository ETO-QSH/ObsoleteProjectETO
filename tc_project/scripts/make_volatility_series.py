import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

base = Path('.')
input_path = base / 'data' / 'processed' / 'merged_data.csv'
out_path = base / 'report' / 'figures' / 'volatility_series.png'
out_path.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(input_path, usecols=['时间', '收盘价'])
df['时间'] = pd.to_datetime(df['时间'], errors='coerce')
df['收盘价'] = pd.to_numeric(df['收盘价'], errors='coerce')
df = df.sort_values('时间').dropna(subset=['时间', '收盘价']).reset_index(drop=True)

# 以5分钟收盘价收益率的滚动标准差近似刻画波动率
ret = df['收盘价'].pct_change().fillna(0)
df['波动率'] = ret.rolling(window=20, min_periods=1).std().fillna(0)

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(df['时间'], df['波动率'], color='#2ca02c', linewidth=1.0, alpha=0.9)
ax.set_title('滚动波动率变化')
ax.set_xlabel('时间')
ax.set_ylabel('波动率')
fig.autofmt_xdate()
plt.tight_layout()
fig.savefig(out_path, dpi=300, bbox_inches='tight')
plt.close(fig)
print(out_path)
