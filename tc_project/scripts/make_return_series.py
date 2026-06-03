import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

base = Path('.')
input_path = base / 'data' / 'processed' / 'merged_data.csv'
out_path = base / 'report' / 'figures' / 'features' / 'return_series.png'
out_path.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(input_path, usecols=['时间', '收盘价'])
df['时间'] = pd.to_datetime(df['时间'], errors='coerce')
df['收盘价'] = pd.to_numeric(df['收盘价'], errors='coerce')
df = df.sort_values('时间').dropna(subset=['时间', '收盘价']).reset_index(drop=True)
df['收益率'] = df['收盘价'].pct_change().fillna(0)

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(figsize=(12, 4.8))
ax.plot(df['时间'], df['收益率'], color='#2f6fdb', linewidth=0.8, alpha=0.85)
ax.axhline(0, color='black', linewidth=1.0, alpha=0.6)
ax.set_title('收益率时间序列')
ax.set_xlabel('时间')
ax.set_ylabel('收益率')
fig.autofmt_xdate()
plt.tight_layout()
fig.savefig(out_path, dpi=300, bbox_inches='tight')
plt.close(fig)
print(out_path)
