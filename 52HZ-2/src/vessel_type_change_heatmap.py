import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

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


def read_and_filter(path, filename):
    df = pd.read_csv(path + filename)
    df['DateTime'] = pd.to_datetime(df['DateTime'])
    df['Year'] = df['DateTime'].dt.year
    df['Month'] = df['DateTime'].dt.month
    mask = (df['Month'].isin([3, 4])) & (df['Year'].isin([2025, 2026]))
    df = df[mask].copy()
    df = df.dropna(axis=1, how='all')
    return df


def summarize(df):
    cols = [c for c in vessel_types if c in df.columns]
    return df.groupby('Year')[cols].mean()


all_arrivals = {}

for name, path in channels.items():
    try:
        df_arr = read_and_filter(path, 'Transit Calls/arrivals-of-ships.csv')
        all_arrivals[name] = summarize(df_arr)
    except Exception as e:
        print(f"[警告] {name} 读取Transit Calls失败: {e}")
        all_arrivals[name] = None

change_records = []
for name, data in all_arrivals.items():
    if data is None or data.empty:
        continue
    for vt in data.columns:
        v25 = data.loc[2025, vt] if 2025 in data.index else 0
        v26 = data.loc[2026, vt] if 2026 in data.index else 0
        if v25 > 0:
            change_records.append({
                'Channel': name,
                'Vessel Type': vt,
                'Change Rate (%)': (v26 - v25) / v25 * 100
            })

df_change = pd.DataFrame(change_records)
if not df_change.empty:
    pivot = df_change.pivot(index='Channel', columns='Vessel Type', values='Change Rate (%)')
    pivot = pivot[[c for c in vessel_types if c in pivot.columns]]

    fig, ax = plt.subplots(figsize=(10, 5))
    im = ax.imshow(pivot.values, cmap='RdYlGn', aspect='auto', vmin=-100, vmax=50)

    ax.set_xticks(np.arange(len(pivot.columns)))
    ax.set_yticks(np.arange(len(pivot.index)))
    ax.set_xticklabels(pivot.columns, fontsize=10)
    ax.set_yticklabels(pivot.index, fontsize=10)

    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            val = pivot.values[i, j]
            if not np.isnan(val):
                text_color = 'white' if abs(val) > 50 else 'black'
                ax.text(j, i, f'{val:.0f}%', ha='center', va='center',
                        color=text_color, fontsize=10, fontweight='bold')

    plt.colorbar(im, ax=ax, label='变化率 (%)', shrink=0.8)
    ax.set_title('各海峡分船型过境到港量变化率（2026 vs 2025）', fontsize=13, fontweight='bold', pad=15)
    plt.tight_layout()

    plt.savefig(f'{output_dir}vessel_type_change_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()

print(f"图表已保存至: {output_dir}vessel_type_change_heatmap.png")
