import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import numpy as np

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def plot_daily_pred_vs_true(csv_file, output_root, window_days=3):
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f'未找到文件: {csv_file}')

    df = pd.read_csv(csv_file)
    required_cols = {'时间', '真实值', '预测值'}
    if not required_cols.issubset(df.columns):
        raise ValueError(f'{csv_file} 缺少必要列: {required_cols - set(df.columns)}')

    df['时间'] = pd.to_datetime(df['时间'])
    df = df.sort_values('时间').reset_index(drop=True)
    df['日期'] = df['时间'].dt.date

    stem = os.path.splitext(os.path.basename(csv_file))[0]
    out_dir = os.path.join(output_root, stem)
    os.makedirs(out_dir, exist_ok=True)

    dates = sorted(df['日期'].unique())
    if len(dates) < window_days:
        raise ValueError(f'{csv_file} 可用交易日不足 {window_days} 天，无法生成滑窗图')

    saved = []
    for start_idx in range(0, len(dates) - window_days + 1):
        window_dates = dates[start_idx:start_idx + window_days]
        window_df = df[df['日期'].isin(window_dates)].copy()
        if window_df.empty:
            continue

        window_df = window_df.sort_values('时间').reset_index(drop=True)
        window_df['effective_x'] = np.arange(len(window_df))
        day_starts = window_df.groupby('日期')['effective_x'].first()
        day_labels = [str(d) for d in day_starts.index]

        fig, axes = plt.subplots(2, 1, figsize=(15, 8), sharex=True)
        fig.suptitle(f'{stem} - {window_dates[0]} 至 {window_dates[-1]} 三日滑窗预测对比', fontsize=15, fontweight='bold')

        axes[0].plot(window_df['effective_x'], window_df['真实值'], label='真实值', color='gray', linewidth=1.8)
        axes[0].plot(window_df['effective_x'], window_df['预测值'], label='预测值', color='#d62728', linewidth=1.8, linestyle='--')
        for boundary in day_starts.iloc[1:]:
            axes[0].axvline(boundary, color='black', linestyle=':', alpha=0.25, linewidth=1)
        axes[0].set_ylabel('数值')
        axes[0].legend(loc='upper left')
        axes[0].grid(True, linestyle='--', alpha=0.5)

        error = window_df['预测值'] - window_df['真实值']
        axes[1].plot(window_df['effective_x'], error, label='预测误差', color='#1f77b4', linewidth=1.5)
        axes[1].axhline(0, color='black', linewidth=1)
        for boundary in day_starts.iloc[1:]:
            axes[1].axvline(boundary, color='black', linestyle=':', alpha=0.25, linewidth=1)
        axes[1].set_xlabel('有效数据点序列')
        axes[1].set_ylabel('误差')
        axes[1].legend(loc='upper left')
        axes[1].grid(True, linestyle='--', alpha=0.5)

        tick_positions = day_starts.values.tolist()
        if len(tick_positions) > 0:
            axes[1].set_xticks(tick_positions)
            axes[1].set_xticklabels(day_labels, rotation=0)

        plt.tight_layout(rect=[0, 0.03, 1, 0.96])
        file_name = f'{window_dates[0]}_to_{window_dates[-1]}.png'
        save_path = os.path.join(out_dir, file_name)
        plt.savefig(save_path, dpi=250)
        plt.close()
        saved.append(save_path)

    return saved


def main():
    parser = argparse.ArgumentParser(description='按天生成 pred_vs_true 预测图')
    parser.add_argument('--input', nargs='*', default=None, help='输入预测 csv 文件列表，默认扫描 outputs/prediction 下的 predictions_*.csv')
    parser.add_argument('--output-root', default='d:/Desktop/Desktop/数学建模/tc_project/outputs/prediction/daily_pred_vs_true', help='输出根目录')
    parser.add_argument('--window-days', type=int, default=3, help='每张图覆盖的天数')
    args = parser.parse_args()

    if args.input:
        csv_files = args.input
    else:
        csv_files = sorted(glob.glob('d:/Desktop/Desktop/数学建模/tc_project/outputs/prediction/predictions_*.csv'))

    all_saved = []
    for csv_file in csv_files:
        try:
            saved = plot_daily_pred_vs_true(csv_file, args.output_root, args.window_days)
            all_saved.extend(saved)
            print(f'[OK] {csv_file} -> {len(saved)} 张图')
        except Exception as exc:
            print(f'[SKIP] {csv_file}: {exc}')

    print(f'总共生成 {len(all_saved)} 张按日对比图')


if __name__ == '__main__':
    main()
