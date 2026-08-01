import matplotlib
matplotlib.use('TkAgg')

import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

plt.rcParams['font.sans-serif'] = ['Lolita']
plt.rcParams['axes.unicode_minus'] = False


def parse_ym(ym_str):
    s = str(ym_str).strip()
    if s.lower() in ('nan', 'nat', 'none', ''):
        return pd.NaT
    try:
        s = s.replace('M', '-').replace('m', '-')
        year, month = s.split('-', 1)
        return pd.Timestamp(year=int(year), month=int(month), day=1)
    except Exception:
        return pd.NaT


def plot_combined_overview(file_paths_eia: dict, excel_path: str, save_path: str = None):
    data_eia = {}
    for name, path in file_paths_eia.items():
        df = pd.read_csv(path)
        df['period'] = pd.to_datetime(df['period'])
        df = df.sort_values('period')
        data_eia[name] = df

    df_raw = pd.read_excel(excel_path, header=0)
    df_comm = df_raw.iloc[2:].copy().reset_index(drop=True)

    df_comm['period'] = df_comm['Commodity'].apply(parse_ym)
    df_comm = df_comm.dropna(subset=['period']).copy()

    df_comm = df_comm[
        (df_comm['period'] >= '2025-01-01') &
        (df_comm['period'] <= '2026-05-31')
    ].sort_values('period').reset_index(drop=True)

    for col in df_comm.columns:
        if col not in ('period', 'Commodity'):
            df_comm[col] = pd.to_numeric(df_comm[col], errors='coerce')

    CRUDE_CONFIG = [
        ('POILAPSP', 'Crude Oil Price Index (2016=100)', '#333333', 2.0, '--'),
        ('POILBRE',  'Brent (Europe)', '#1f77b4', 1.5, '-'),
        ('POILDUB',  'Dubai Fateh (Middle East)', '#d62728', 1.5, '-'),
        ('POILWTI',  'WTI (US)', '#ff7f0e', 1.5, '-'),
    ]

    GAS_CONFIG = [
        ('PNGAS',    'Natural Gas Price Index (2016=100)', '#333333', 2.0, '--'),
        ('PNGASEU',  'TTF (Europe)', '#9467bd', 1.5, '-'),
        ('PNGASJP',  'Indonesian LNG in Japan (Asia)', '#d62728', 1.5, '-'),
        ('PNGASUS',  'Henry Hub (US)', '#2ca02c', 1.5, '-'),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(24, 12))
    fig.suptitle('Energy Market Overview (2025–2026)', fontsize=18, fontweight='bold', y=0.92)

    ax1 = axes[0, 0]
    for name, color, label in [('Brent', '#1f77b4', 'Brent Spot Price'), ('WTI', '#ff7f0e', 'WTI Spot Price')]:
        if name in data_eia:
            ax1.plot(data_eia[name]['period'], data_eia[name]['value'], label=label, color=color, linewidth=1.2)

    ax1.set_title('Crude Oil Spot Prices (EIA)', fontsize=13, fontweight='bold')
    ax1.set_ylabel('USD / Barrel')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)

    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=30, ha='right')

    ax2 = axes[0, 1]
    if 'HenryHub' in data_eia:
        ax2.plot(data_eia['HenryHub']['period'], data_eia['HenryHub']['value'], color='#2ca02c', linewidth=1.2, label='Henry Hub Spot Price')

    ax2.set_title('Natural Gas Spot Price (EIA)', fontsize=13, fontweight='bold')
    ax2.set_ylabel('USD / MMBtu')
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.3)

    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=30, ha='right')

    ax3 = axes[1, 0]
    for name, color, label in [('CrudeProduction', '#d62728', 'U.S. Field Production'), ('RefineryInput', '#9467bd', 'U.S. Refinery Net Input')]:
        if name in data_eia:
            ax3.plot(data_eia[name]['period'], data_eia[name]['value'], label=label, color=color, linewidth=1.5, marker='o', markersize=3)

    ax3.set_title('U.S. Crude Production & Refinery Input', fontsize=13, fontweight='bold')
    ax3.set_ylabel('Thousand Barrels / Day')
    ax3.legend(loc='upper left')
    ax3.grid(True, alpha=0.3)

    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax3.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=30, ha='right')

    ax4 = axes[1, 1]
    if 'CrudeExport' in data_eia:
        ax4.plot(data_eia['CrudeExport']['period'], data_eia['CrudeExport']['value'], color='#8c564b', linewidth=1.5, marker='s', markersize=3, label='U.S. Ending Stocks excl. SPR')

    ax4.set_title('U.S. Crude Oil Ending Stocks (excl. SPR)', fontsize=13, fontweight='bold')
    ax4.set_ylabel('Thousand Barrels')
    ax4.legend(loc='upper left')
    ax4.grid(True, alpha=0.3)

    ax4.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax4.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.setp(ax4.xaxis.get_majorticklabels(), rotation=30, ha='right')

    def _plot_panel(ax, config, title, ylabel):
        plotted = False
        for code, label, color, lw, ls in config:
            if code in df_comm.columns and not df_comm[code].isna().all():
                ax.plot(df_comm['period'], df_comm[code], label=label, color=color, linewidth=lw, linestyle=ls, marker='o', markersize=3)
                plotted = True
            else:
                print(f"  ⚠ 列未找到或全空: {code} ({label})")
        if not plotted:
            ax.text(0.5, 0.5, 'Columns not found in Excel', ha='center', va='center', transform=ax.transAxes, fontsize=12, color='red')

        ax.set_title(title, fontsize=13, fontweight='bold')
        ax.set_ylabel(ylabel)
        ax.legend(loc='upper left', fontsize=9)
        ax.grid(True, alpha=0.3)

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

    _plot_panel(axes[0, 2], CRUDE_CONFIG, 'Crude Oil Market Impact', 'USD / Barrel  or  Index (2016=100)')
    _plot_panel(axes[1, 2], GAS_CONFIG, 'Natural Gas Market Impact', 'USD / MMBtu  or  Index (2016=100)')

    plt.tight_layout(rect=[0, 0, 1, 0.92])
    plt.savefig(save_path, dpi=200, bbox_inches='tight')


if __name__ == '__main__':
    output = "../output/energy_map/"
    path_eia = "../external/EIA/data/"
    excel_file = "../external/IMF/World Bank Commodity Price Data.xlsx"

    Path(output).mkdir(exist_ok=True)

    file_dict_eia = {
        'Brent': path_eia + 'Brent_daily.csv',
        'WTI': path_eia + 'WTI_daily.csv',
        'HenryHub': path_eia + 'HenryHub_daily.csv',
        'CrudeExport': path_eia + 'CrudeExport_weekly.csv',
        'CrudeProduction': path_eia + 'CrudeProduction_weekly.csv',
        'RefineryInput': path_eia + 'RefineryInput_weekly.csv'
    }

    plot_combined_overview(
        file_paths_eia=file_dict_eia,
        excel_path=excel_file,
        save_path=output+'energy_overview_with_commodity.png'
    )
