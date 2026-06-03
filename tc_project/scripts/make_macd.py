import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

base = Path('.')
input_path = base / 'data' / 'processed' / 'merged_data.csv'
out_path = base / 'report' / 'figures' / 'macd.png'
out_path.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(input_path, usecols=['时间', '收盘价'])
df['时间'] = pd.to_datetime(df['时间'], errors='coerce')
df['收盘价'] = pd.to_numeric(df['收盘价'], errors='coerce')
df = df.sort_values('时间').dropna(subset=['时间', '收盘价']).reset_index(drop=True)

close = df['收盘价']
ema12 = close.ewm(span=12, adjust=False).mean()
ema26 = close.ewm(span=26, adjust=False).mean()
dif = ema12 - ema26
dea = dif.ewm(span=9, adjust=False).mean()
macd_hist = 2 * (dif - dea)

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), sharex=True, gridspec_kw={'height_ratios': [2, 1]})

ax1.plot(df['时间'], close, color='#444444', linewidth=0.8, alpha=0.65, label='收盘价')
ax1.plot(df['时间'], ema12, color='#d62728', linewidth=1.3, label='EMA12')
ax1.plot(df['时间'], ema26, color='#1f77b4', linewidth=1.3, label='EMA26')
ax1.set_title('MACD 指标变化')
ax1.set_ylabel('价格')
ax1.legend(frameon=False, ncol=3, loc='upper left')

colors = ['#d62728' if v >= 0 else '#1f77b4' for v in macd_hist]
ax2.bar(df['时间'], macd_hist, color=colors, width=0.01, alpha=0.8)
ax2.plot(df['时间'], dif, color='#ff7f0e', linewidth=1.0, label='DIF')
ax2.plot(df['时间'], dea, color='#2ca02c', linewidth=1.0, label='DEA')
ax2.axhline(0, color='black', linewidth=0.8, alpha=0.7)
ax2.set_ylabel('MACD')
ax2.set_xlabel('时间')
ax2.legend(frameon=False, ncol=3, loc='upper left')

fig.autofmt_xdate()
plt.tight_layout()
fig.savefig(out_path, dpi=300, bbox_inches='tight')
plt.close(fig)
print(out_path)
