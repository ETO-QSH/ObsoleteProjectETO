import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['Lolita']
plt.rcParams['axes.unicode_minus'] = False

base_national = '../external/PORTWATCH/Calls/National/'
base_port = '../external/PORTWATCH/Calls/Port/'
output_dir = '../output/transit_map/'
Path(output_dir).mkdir(exist_ok=True)

countries = [
    'China', 'India', 'Iraq', 'Japan', 'Kuwait', 'Qatar',
    'Saudi Arabia', 'South Korea', 'The Netherlands',
    'United Arab Emirates', 'United States'
]

ports = [
    'Fujairah', 'Kharg Island', 'Mina Al Ahmadi', 'Mundra',
    'Ningbo', 'Qingdao', 'Ras Laffan', 'Ras Tanura',
    'Rotterdam', 'Shanghai', 'Singapore', 'Trieste'
]

start_date = pd.Timestamp('2025-01-01')
end_date = pd.Timestamp('2026-07-07')


def read_shipment(path, filename):
    df = pd.read_csv(path + filename)
    df['DateTime'] = pd.to_datetime(df['DateTime'])
    mask = (df['DateTime'] >= start_date) & (df['DateTime'] <= end_date)
    df = df[mask].copy().sort_values('DateTime')
    df['Week'] = df['DateTime'].dt.to_period('W').dt.start_time
    weekly = df.groupby('Week')['Tanker'].sum().reset_index()
    weekly.columns = ['DateTime', 'Tanker']
    return weekly


def calc_net(names, base_path):
    exporters = {}
    importers = {}
    for name in names:
        try:
            out_df = read_shipment(f'{base_path}{name}/', 'Outgoing Shipment/outgoing-shipment.csv')
        except Exception:
            out_df = pd.DataFrame(columns=['DateTime', 'Tanker'])
        try:
            in_df = read_shipment(f'{base_path}{name}/', 'Incoming Shipment/incoming-shipment.csv')
        except Exception:
            in_df = pd.DataFrame(columns=['DateTime', 'Tanker'])

        net_df = pd.merge(
            out_df.rename(columns={'Tanker': 'Out'}),
            in_df.rename(columns={'Tanker': 'In'}),
            on='DateTime', how='outer'
        ).fillna(0)
        net_df['Net'] = net_df['Out'] - net_df['In']
        net_df = net_df[['DateTime', 'Net']].sort_values('DateTime').reset_index(drop=True)

        total_net = net_df['Net'].sum()
        if total_net > 0:
            exporters[name] = net_df
        elif total_net < 0:
            net_df['Net'] = -net_df['Net']
            importers[name] = net_df
    return exporters, importers


nat_exp, nat_imp = calc_net(countries, base_national)
port_exp, port_imp = calc_net(ports, base_port)


def top5(data_dict):
    sorted_items = sorted(data_dict.items(), key=lambda x: x[1]['Net'].sum(), reverse=True)
    return dict(sorted_items[:5])


nat_exp_top5 = top5(nat_exp)
port_exp_top5 = top5(port_exp)
nat_imp_top5 = top5(nat_imp)
port_imp_top5 = top5(port_imp)

fig, axes = plt.subplots(2, 2, figsize=(16, 10), sharex=False, sharey=False)
axes = axes.flatten()

titles = [
    '净出口国石油流量 TOP5',
    '净进口国石油流量 TOP5',
    '净出口港石油流量 TOP5',
    '净进口港石油流量 TOP5',
]

datasets = [nat_exp_top5, nat_imp_top5, port_exp_top5, port_imp_top5]
colors = plt.cm.tab20(np.linspace(0, 1, 20))

for idx, (ax, title, data) in enumerate(zip(axes, titles, datasets)):
    if not data:
        ax.set_visible(False)
        continue

    for i, (name, df) in enumerate(data.items()):
        ax.plot(df['DateTime'], df['Net'], label=name, linewidth=1.8, alpha=0.9, color=colors[i % 20], marker='o', markersize=3)

    ax.set_title(title, fontsize=12, fontweight='bold', color='#2C3E50', pad=10)
    ax.set_ylabel('周油轮净流量 (Tanker)', fontsize=10, color='#2C3E50')
    ax.grid(axis='y', alpha=0.3, color='#CCCCCC', linestyle='-')
    ax.grid(axis='x', alpha=0.15, color='#CCCCCC', linestyle='-')

    ax.legend(fontsize=9, loc='upper left', ncol=1, frameon=True, fancybox=True, edgecolor='#DDDDDD', facecolor='white', columnspacing=1.0)

    ax.tick_params(axis='x', rotation=25, labelsize=8, colors='#666666')
    ax.tick_params(axis='y', labelsize=9, colors='#666666')

    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    for spine in ['left', 'bottom']:
        ax.spines[spine].set_color('#CCCCCC')

fig.suptitle('2025–2026年“中东—国际市场”油轮净进出口周流量折线图', fontsize=14, fontweight='bold', color='#2C3E50', y=0.92)

plt.tight_layout(rect=[0, 0, 1, 0.92])
output_path = f'{output_dir}oil_net_trade_flow_weekly_top5.png'
fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
plt.close(fig)

print(f"\n图表已保存至: {output_path}")
