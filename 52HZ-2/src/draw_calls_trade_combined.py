import io
import math
import numpy as np
import pandas as pd
from PIL import Image
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

plt.rcParams['font.sans-serif'] = ['Lolita']
plt.rcParams['axes.unicode_minus'] = False

MAIN_START = '2026-01-01'
MAIN_END = '2026-06-30'

COLORS = {
    'Container': '#C41E3A',
    'Dry Bulk': '#F4A261',
    'General Cargo': '#F4D35E',
    'Roll-on/roll-off': '#90E0EF',
    'Tanker': '#2D6A4F',
}
MA_COLOR = '#E9A319'
PRIOR_MA_COLOR = '#444444'
HIGHLIGHT_COLOR = '#7B9ED9'

SHIP_TYPES = ['Container', 'Dry Bulk', 'General Cargo', 'Roll-on/roll-off', 'Tanker']


def smart_yticks(ax, data_max, num_ticks=4):
    if data_max <= 0:
        ax.set_yticks([0])
        return [0]
    rough = data_max / (num_ticks - 1) if num_ticks > 1 else data_max
    exp = 10 ** math.floor(math.log10(rough))
    frac = rough / exp
    if frac <= 1:
        step = exp
    elif frac <= 2:
        step = 2 * exp
    elif frac <= 5:
        step = 5 * exp
    else:
        step = 10 * exp
    max_tick = math.ceil(data_max / step) * step
    ticks = list(np.arange(0, max_tick + step, step))
    while len(ticks) > num_ticks + 1:
        ticks = ticks[::2]
    ax.set_yticks(ticks)
    return ticks


def make_y_formatter(global_max):
    def y_fmt(v, _):
        if v == 0:
            return '0'
        if global_max >= 1e6:
            return f'{v / 1e6:.1f}M'
        elif global_max >= 1e3:
            return f'{v / 1e3:.0f}K'
        else:
            return f'{v:.0f}'
    return y_fmt


def render_chart(csv_path, title):
    df = pd.read_csv(csv_path)
    df['DateTime'] = pd.to_datetime(df['DateTime'])
    df = df.sort_values('DateTime').reset_index(drop=True)

    fig = plt.figure(figsize=(16, 6.5))
    ax_main = fig.add_axes([0.09, 0.42, 0.89, 0.36])
    ax_mini = fig.add_axes([0.09, 0.13, 0.89, 0.22])

    main_start = pd.Timestamp(MAIN_START)
    main_end = pd.Timestamp(MAIN_END)
    mask = (df['DateTime'] >= main_start) & (df['DateTime'] <= main_end)
    df_main = df[mask].copy()

    x = np.arange(len(df_main))
    bottom = np.zeros(len(df_main))
    for ship in reversed(SHIP_TYPES):
        ax_main.bar(x, df_main[ship].values, bottom=bottom, color=COLORS[ship], width=0.85, edgecolor='white', linewidth=0.15)
        bottom += df_main[ship].values

    ax_main.plot(x, df_main['7-day Moving Average'].values, color=MA_COLOR, linewidth=2.2, zorder=5)
    ax_main.plot(x, df_main['Prior Year: 7-day Moving Average'].values, color=PRIOR_MA_COLOR, linewidth=1.8, linestyle='--', zorder=5)

    main_max = df_main[SHIP_TYPES].sum(axis=1).max()
    smart_yticks(ax_main, main_max, num_ticks=4)
    ax_main.yaxis.set_major_formatter(plt.FuncFormatter(make_y_formatter(main_max)))
    ax_main.tick_params(axis='y', labelsize=10, colors='#666666')
    ax_main.set_ylabel('')

    ax_main.set_xlim(-1, len(df_main))
    month_ticks, month_labels = [], []
    for i, d in enumerate(df_main['DateTime']):
        if d.day <= 3 or i == 0:
            if i == 0 or d.month != df_main['DateTime'].iloc[max(0, i - 1)].month:
                month_ticks.append(i)
                month_labels.append(f"{d.year}年{d.month}月")

    ax_main.set_xticks(month_ticks)
    ax_main.set_xticklabels(month_labels, fontsize=10, color='#666666')
    ax_main.tick_params(axis='x', length=4, colors='#666666')

    ax_main.grid(axis='y', alpha=0.3, color='#CCCCCC', linestyle='-')
    ax_main.set_axisbelow(True)
    for spine in ['top', 'right']:
        ax_main.spines[spine].set_visible(False)
    for spine in ['left', 'bottom']:
        ax_main.spines[spine].set_color('#CCCCCC')

    x_all = np.arange(len(df))
    for ship in SHIP_TYPES:
        ax_mini.plot(
            x_all,
            df[ship].values,
            color=COLORS[ship],
            linewidth=0.8,
            alpha=0.8
        )

    ax_mini.plot(
        x_all,
        df['7-day Moving Average'].values,
        color=MA_COLOR,
        linewidth=0.9,
        alpha=0.9
    )

    ax_mini.plot(
        x_all,
        df['Prior Year: 7-day Moving Average'].values,
        color=PRIOR_MA_COLOR,
        linewidth=0.9,
        linestyle='--',
        alpha=0.9
    )

    total_all = df[SHIP_TYPES].sum(axis=1)
    ax_mini.fill_between(x_all, 0, df['7-day Moving Average'].values, color=MA_COLOR, alpha=0.12)

    ax_mini.set_xlim(0, len(df))
    ax_mini.set_ylim(0, total_all.max() * 1.1)

    start_idx = df[df['DateTime'] >= main_start].index[0]
    end_idx = df[df['DateTime'] <= main_end].index[-1]

    rect = mpatches.Rectangle(
        (start_idx / len(df), 0),
        (end_idx - start_idx) / len(df),
        height=1,
        transform=ax_mini.transAxes,
        linewidth=1.5,
        edgecolor=HIGHLIGHT_COLOR,
        facecolor=HIGHLIGHT_COLOR,
        alpha=0.2,
        zorder=3
    )

    ax_mini.add_patch(rect)
    for pos in [start_idx, end_idx]:
        ax_mini.axvline(x=pos, color=HIGHLIGHT_COLOR, linewidth=2, alpha=0.8, zorder=4)

    year_ticks, year_labels = [], []
    for i, d in enumerate(df['DateTime']):
        if d.month == 1 and d.day == 1:
            year_ticks.append(i)
            year_labels.append(f"{d.year}年")

    ax_mini.set_xticks(year_ticks)
    ax_mini.set_xticklabels(year_labels, fontsize=9, color='#999999')
    ax_mini.tick_params(axis='x', length=3, colors='#999999')

    mini_max = total_all.max() * 1.1
    smart_yticks(ax_mini, mini_max, num_ticks=4)
    ax_mini.yaxis.set_major_formatter(plt.FuncFormatter(make_y_formatter(mini_max)))
    ax_mini.tick_params(axis='y', labelsize=8, colors='#999999')
    ax_mini.set_ylabel('')

    for spine in ['top', 'right']:
        ax_mini.spines[spine].set_visible(False)
    for spine in ['left', 'bottom']:
        ax_mini.spines[spine].set_color('#CCCCCC')
    ax_mini.set_facecolor('#FAFAFA')

    fig.suptitle(title, fontsize=14, fontweight='bold', color='#333333', y=0.84)

    legend_items = [
        mpatches.Patch(facecolor=COLORS['Container'], label='Container'),
        mpatches.Patch(facecolor=COLORS['Dry Bulk'], label='Dry Bulk'),
        mpatches.Patch(facecolor=COLORS['General Cargo'], label='General Cargo'),
        mpatches.Patch(facecolor=COLORS['Roll-on/roll-off'], label='Roll-on/roll-off'),
        mpatches.Patch(facecolor=COLORS['Tanker'], label='Tanker'),
        plt.Line2D([0], [0], color=MA_COLOR, linewidth=2.2, label='7-day Moving Average'),
        plt.Line2D([0], [0], color=PRIOR_MA_COLOR, linewidth=1.8, linestyle='--', label='Prior Year: 7-day Moving Average'),
    ]

    fig.legend(
        handles=legend_items,
        loc='upper center',
        bbox_to_anchor=(0.5, 0.1),
        ncol=7,
        fontsize=9,
        frameon=False,
        columnspacing=1.8
    )

    buf = io.BytesIO()
    fig.savefig(buf, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)
    buf.seek(0)

    return Image.open(buf)


def combine_charts(
    calls_path, trade_path, calls_title='Strait of Hormuz Transit Calls',
    trade_title='Strait of Hormuz Transit Trade Volume', output_path='combined.png'
):
    img_calls = render_chart(calls_path, calls_title)
    img_trade = render_chart(trade_path, trade_title)

    W = max(img_calls.width, img_trade.width)
    H = max(img_calls.height, img_trade.height)

    combined = Image.new('RGB', (W, H * 2 + 10), 'white')
    combined.paste(img_calls, (W - img_calls.width, 0))
    combined.paste(img_trade, (W - img_trade.width, H + 10))

    combined.save(output_path, dpi=(150, 150))
    return output_path


if __name__ == '__main__':
    path = '../external/PORTWATCH/Calls/Channel/Strait of Hormuz/'
    output = '../output/transit_map/'
    Path(output).mkdir(exist_ok=True)
    combine_charts(
        path + 'Transit Calls/arrivals-of-ships.csv',
        path + 'Transit Trade Volume/chart.csv',
        path.split('/')[-2] + ' Transit Calls',
        path.split('/')[-2] + ' Transit Trade Volume',
        f'{output}{path.split('/')[-2].lower().replace(' ', '_')}_combined.png'
    )
