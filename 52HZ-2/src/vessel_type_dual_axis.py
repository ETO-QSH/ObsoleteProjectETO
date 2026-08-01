import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

plt.rcParams['font.sans-serif'] = ['Lolita']
plt.rcParams['axes.unicode_minus'] = False

channels = {
    'Strait of Hormuz': '../external/PORTWATCH/Calls/Channel/Strait of Hormuz/',
    'Cape of Good Hope': '../external/PORTWATCH/Calls/Channel/Cape of Good Hope/',
    'Malacca Strait': '../external/PORTWATCH/Calls/Channel/Malacca Strait/',
    'Suez Canal': '../external/PORTWATCH/Calls/Channel/Suez Canal/',
}

output_dir = '../output/transit_map/'
Path(output_dir).mkdir(exist_ok=True)

vessel_types = ['Container', 'Dry Bulk', 'General Cargo', 'Roll-on/roll-off', 'Tanker']

COLORS = {
    'Container': '#5DADE2',
    'Dry Bulk': '#F5B041',
    'General Cargo': '#58D68D',
    'Roll-on/roll-off': '#85C1E9',
    'Tanker': '#48C9B0',
}

DARK_COLOR = '#2C3E50'


def read_and_filter(path, filename):
    df = pd.read_csv(path + filename)
    df['DateTime'] = pd.to_datetime(df['DateTime'])
    df['Year'] = df['DateTime'].dt.year
    df['Month'] = df['DateTime'].dt.month
    mask = (df['Month'].isin([3, 4])) & (df['Year'].isin([2025, 2026]))
    df = df[mask].copy()
    cols = [c for c in vessel_types if c in df.columns]
    return df.groupby('Year')[cols].mean()


all_arrivals = {}
all_trade = {}

for name, path in channels.items():
    try:
        all_arrivals[name] = read_and_filter(path, 'Transit Calls/arrivals-of-ships.csv')
    except Exception as e:
        print(f"[警告] {name} Transit Calls: {e}")
        all_arrivals[name] = None
    try:
        all_trade[name] = read_and_filter(path, 'Transit Trade Volume/chart.csv')
    except Exception as e:
        print(f"[警告] {name} Trade Volume: {e}")
        all_trade[name] = None


def trade_formatter(x):
    if x >= 1e6:
        return f'{x / 1e6:.0f}M'
    elif x >= 1e3:
        return f'{x / 1e3:.0f}K'
    else:
        return f'{x:.0f}'


fig, ax1 = plt.subplots(figsize=(12, 8))
ax2 = ax1.twinx()

channel_names = list(channels.keys())
x = np.arange(len(channel_names))

for i, ch in enumerate(channel_names):
    data = all_arrivals[ch]
    if data is None:
        continue

    if 2025 in data.index:
        bottom = 0
        for vt in vessel_types:
            if vt in data.columns:
                v = data.loc[2025, vt]
                ax1.bar(x[i] - 0.28, v, 0.14, bottom=bottom, color=COLORS[vt], alpha=0.45, edgecolor='white', linewidth=0.3)
                bottom += v
        if bottom > 0:
            ax1.annotate(f'{bottom:.0f}', xy=(x[i] - 0.28, bottom), ha='center', va='bottom', fontsize=7, color='#888888', fontweight='bold')

    if 2026 in data.index:
        bottom = 0
        for vt in vessel_types:
            if vt in data.columns:
                v = data.loc[2026, vt]
                ax1.bar(x[i] - 0.12, v, 0.14, bottom=bottom, color=COLORS[vt], alpha=1.0, edgecolor='white', linewidth=0.3)
                bottom += v
        if bottom > 0:
            ax1.annotate(f'{bottom:.0f}', xy=(x[i] - 0.12, bottom), ha='center', va='bottom', fontsize=7, color='#333333', fontweight='bold')

for i, ch in enumerate(channel_names):
    data = all_trade[ch]
    if data is None:
        continue

    if 2025 in data.index:
        bottom = 0
        for vt in vessel_types:
            if vt in data.columns:
                v = data.loc[2025, vt]
                ax2.bar(x[i] + 0.12, v, 0.14, bottom=bottom, color=COLORS[vt], alpha=0.45, edgecolor='white', linewidth=0.3)
                bottom += v
        if bottom > 0:
            if bottom >= 1e6:
                label = f'{bottom / 1e6:.1f}M'
            elif bottom >= 1e3:
                label = f'{bottom / 1e3:.0f}K'
            else:
                label = f'{bottom:.0f}'
            ax2.annotate(label, xy=(x[i] + 0.12, bottom), ha='center', va='bottom', fontsize=7, color='#888888', fontweight='bold')

    if 2026 in data.index:
        bottom = 0
        for vt in vessel_types:
            if vt in data.columns:
                v = data.loc[2026, vt]
                ax2.bar(x[i] + 0.28, v, 0.14, bottom=bottom, color=COLORS[vt], alpha=1.0, edgecolor='white', linewidth=0.3)
                bottom += v
        if bottom > 0:
            if bottom >= 1e6:
                label = f'{bottom / 1e6:.1f}M'
            elif bottom >= 1e3:
                label = f'{bottom / 1e3:.0f}K'
            else:
                label = f'{bottom:.0f}'
            ax2.annotate(label, xy=(x[i] + 0.28, bottom), ha='center', va='bottom', fontsize=7, color='#333333', fontweight='bold')

ax1.set_xticks(x)
ax1.set_xticklabels(channel_names, fontsize=11, color=DARK_COLOR)
ax1.tick_params(axis='x', length=0, pad=12)

ax1.set_ylabel('日均过境船舶数', fontsize=12, color=DARK_COLOR, fontweight='bold')
ax2.set_ylabel('日均过境贸易量', fontsize=12, color=DARK_COLOR, fontweight='bold')

ax1.tick_params(axis='y', labelsize=10, colors=DARK_COLOR)
ax2.tick_params(axis='y', labelsize=10, colors=DARK_COLOR)

ax2.yaxis.set_major_formatter(FuncFormatter(trade_formatter))

ax1.grid(axis='y', alpha=0.3, color='#CCCCCC', linestyle='-', zorder=0)
ax1.set_axisbelow(True)

for spine in ['top']:
    ax1.spines[spine].set_visible(False)
    ax2.spines[spine].set_visible(False)
for spine in ['left', 'right', 'bottom']:
    ax1.spines[spine].set_color('#CCCCCC')
    ax2.spines[spine].set_color('#CCCCCC')

legend_items = []
for vt in vessel_types:
    legend_items.append(plt.Rectangle((0, 0), 1, 1, facecolor=COLORS[vt], edgecolor='white', label=vt))
legend_items.append(plt.Rectangle((0, 0), 1, 1, facecolor='#AAAAAA', alpha=0.45, edgecolor='white', label='2025 (封锁前)'))
legend_items.append(plt.Rectangle((0, 0), 1, 1, facecolor='#333333', alpha=1.0, edgecolor='white', label='2026 (封锁后)'))

fig.legend(handles=legend_items, loc='lower center', bbox_to_anchor=(0.5, 0.025), ncol=7, fontsize=9, frameon=False, columnspacing=1.5)
fig.suptitle('封锁前后各海峡分船型过境对比（2025年3-4月 vs 2026年3-4月）', fontsize=14, fontweight='bold', color=DARK_COLOR, y=0.9)

output_path = f'{output_dir}vessel_type_dual_axis.png'
fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
plt.close(fig)

print(f"图表已保存至: {output_path}")
