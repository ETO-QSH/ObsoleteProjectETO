import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


base = Path('.')
input_path = base / 'data' / 'processed' / 'merged_data.csv'
out_path = base / 'report' / 'figures' / 'intraday_pattern.png'
out_path.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(input_path)
df.columns = df.columns.str.strip()

df['时间'] = pd.to_datetime(df['时间'], errors='coerce')
df['成交量'] = pd.to_numeric(df['成交量'], errors='coerce')
df = df.dropna(subset=['时间', '成交量']).copy()

df['日内时刻'] = df['时间'].dt.strftime('%H:%M')
intraday = df.groupby('日内时刻', as_index=False)['成交量'].mean()
intraday['排序'] = pd.to_datetime(intraday['日内时刻'], format='%H:%M')
intraday = intraday.sort_values('排序')

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(figsize=(12, 5.5))
ax.plot(intraday['日内时刻'], intraday['成交量'], color='#1f77b4', linewidth=2.0)
ax.fill_between(range(len(intraday)), intraday['成交量'].values, color='#1f77b4', alpha=0.12)

tick_step = max(len(intraday) // 8, 1)
tick_positions = list(range(0, len(intraday), tick_step))
ax.set_xticks(tick_positions)
ax.set_xticklabels(intraday['日内时刻'].iloc[tick_positions], rotation=35, ha='right')

ax.set_title('日内波动结构')
ax.set_xlabel('时间')
ax.set_ylabel('平均成交量')

fig.tight_layout()
fig.savefig(out_path, dpi=300, bbox_inches='tight')
plt.close(fig)

print(out_path)