import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import argparse

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.sans-serif'] = ['SimHei']  
plt.rcParams['axes.unicode_minus'] = False 

CSI500_BENCHMARK_FILE = 'd:/Desktop/Desktop/数学建模/tc_project/data/processed/merged_data.csv'
CSI500_BENCHMARK_COL = '中证500指数'


def load_csi500_series(time_index, benchmark_file=CSI500_BENCHMARK_FILE, benchmark_col=CSI500_BENCHMARK_COL):
    benchmark_df = pd.read_csv(benchmark_file, usecols=['时间', benchmark_col])
    benchmark_df['时间'] = pd.to_datetime(benchmark_df['时间'])
    benchmark_df = benchmark_df.sort_values('时间').drop_duplicates('时间')
    benchmark_series = benchmark_df.set_index('时间')[benchmark_col]
    aligned = benchmark_series.reindex(pd.to_datetime(time_index)).ffill().bfill()
    return aligned

def run_backtest(pred_file, initial_capital=1000000, transaction_cost=0.003, mode='normal'):
    if not os.path.exists(pred_file):
        raise FileNotFoundError(f'未找到预测文件 {pred_file}，请先运行预测脚本。')
        
    df = pd.read_csv(pred_file)
    df['时间'] = pd.to_datetime(df['时间'])
    df = df.sort_values('时间').reset_index(drop=True)

    # 对齐中证500指数，作为论文中最关键的外部基准曲线
    df['csi500_price'] = load_csi500_series(df['时间']).values
    df['csi500_capital'] = initial_capital * (df['csi500_price'] / df['csi500_price'].iloc[0])
    df['csi500_return'] = df['csi500_capital'].pct_change().fillna(0)
    
    df['current_price'] = df['真实值']
    df['prev_price'] = df['current_price'].shift(1)
    
    # 为应对高达 0.3% 的手续费，引入迟滞区间（状态机）避免被锯齿频繁洗盘切割
    df['expected_return'] = (df['预测值'] - df['prev_price']) / df['prev_price']
    
    # 只有预期向上大幅拉升（大于双边交易费率容差）才开仓；一旦开仓，只有预期开始走平或者下跌时才平仓
    buy_threshold = transaction_cost * 1.2
    sell_threshold = -0.001
    
    current_pos = 0
    positions = []
    for exp in df['expected_return']:
        if current_pos == 0:
            if exp > buy_threshold:
                current_pos = 1
        else:
            if exp < sell_threshold:
                current_pos = 0
        positions.append(current_pos)
        
    df['target_position'] = positions
    
    df['market_return'] = (df['current_price'] - df['prev_price']) / df['prev_price']
    df['market_return'] = df['market_return'].fillna(0)
    
    df['strategy_return'] = df['target_position'] * df['market_return']
    
    df['position_change'] = df['target_position'].diff().abs()
    df.loc[df['position_change'] == 1, 'strategy_return'] -= transaction_cost
    
    df['strategy_return'] = df['strategy_return'].fillna(0)

    df['strategy_alpha_csi500'] = df['strategy_return'] - df['csi500_return']
    
    df['capital'] = initial_capital * (1 + df['strategy_return']).cumprod()
    df['market_capital'] = initial_capital * (1 + df['market_return']).cumprod()
    
    total_return = (df['capital'].iloc[-1] / initial_capital) - 1
    market_total_return = (df['market_capital'].iloc[-1] / initial_capital) - 1
    
    K_BARS_PER_DAY = 48
    ANNUAL_DAYS = 252
    annual_return = total_return * (ANNUAL_DAYS * K_BARS_PER_DAY / len(df))
    
    df['cummax_capital'] = df['capital'].cummax()
    df['drawdown'] = (df['cummax_capital'] - df['capital']) / df['cummax_capital']
    max_drawdown = df['drawdown'].max()
    
    sharpe_ratio = np.sqrt(ANNUAL_DAYS * K_BARS_PER_DAY) * (df['strategy_return'].mean()) / (df['strategy_return'].std() + 1e-9)
    
    # ======== 以下核心修改：统计按天的报表并绘制四重折线表 ========
    df['Date'] = df['时间'].dt.date
    daily_records = []
    
    for date, group in df.groupby('Date'):
        # 当日最后收盘价
        last_price = group['current_price'].iloc[-1]
        
        # 资金结算与总收益率
        end_capital = group['capital'].iloc[-1]
        date_total_return = (end_capital / initial_capital) - 1
        
        # 市场同期累计收益
        date_market_return = (group['market_capital'].iloc[-1] / initial_capital) - 1
        date_csi500_return = (group['csi500_capital'].iloc[-1] / initial_capital) - 1
        
        # 最大回撤 (截至当日的累计历史最大回撤 / 或当日内最大回撤，这里记当日发生的最大累计回撤)
        date_max_drawdown = group['drawdown'].max()
        
        # 当日的超额收益系列计算(主动收益)
        daily_strategy_ret_seq = group['strategy_return']
        daily_market_ret_seq = group['market_return']
        active_returns = daily_strategy_ret_seq - daily_market_ret_seq
        
        # 信息比率 IR = mean(Active Return) / std(Active Return) 乘以 年化调节(仅算当天的IR度量)
        if active_returns.std() > 1e-8:
            daily_ir = (active_returns.mean() / active_returns.std()) * np.sqrt(K_BARS_PER_DAY)
        else:
            daily_ir = 0.0
            
        daily_records.append({
            '日期': date,
            '最终收盘价': last_price,
            '策略累计收益率': date_total_return,
            '市场平均累计收益': date_market_return,
            '中证500累计收益': date_csi500_return,
            '信息比率(IR)': daily_ir,
            '当日最大回撤': date_max_drawdown
        })
        
    daily_df = pd.DataFrame(daily_records)
    daily_df['日期'] = pd.to_datetime(daily_df['日期'])
    
    # 保存按天报告
    out_dir = 'd:/Desktop/Desktop/数学建模/tc_project/outputs/figures'
    os.makedirs(out_dir, exist_ok=True)
    out_daily_csv = f'd:/Desktop/Desktop/数学建模/tc_project/outputs/prediction/daily_report_{mode}.csv'
    daily_df.to_csv(out_daily_csv, index=False)
    
    # 保存所有的完整操作行为过滤版 (Buy/Sell)
    ops_df = df[df['position_change'] > 0][['时间', 'current_price', 'target_position', 'strategy_return']].copy()
    ops_df['操作类型'] = np.where(ops_df['target_position'] == 1, '买入', '卖出')
    ops_df.rename(columns={'current_price': '成交价格', 'strategy_return': '当下K线收益扣除成本'}, inplace=True)
    out_ops_csv = f'd:/Desktop/Desktop/数学建模/tc_project/outputs/prediction/trade_operations_{mode}.csv'
    ops_df[['时间', '操作类型', '成交价格', '当下K线收益扣除成本']].to_csv(out_ops_csv, index=False)

    # 绘制高级看板四重奏图
    fig, axes = plt.subplots(4, 1, figsize=(15, 16), sharex=False)
    fig.suptitle(f'【量化沙盒】策略表现每日跟踪面板 ({mode.capitalize()} Mode)', fontsize=18, fontweight='bold', y=0.98)
    
    # 图1：主连收盘价与买卖点标记
    axes[0].plot(df['时间'], df['current_price'], color='gray', label='收盘价波动', alpha=0.7)
    buy_pts = df[(df['position_change'] == 1) & (df['target_position'] == 1)]
    sell_pts = df[(df['position_change'] == 1) & (df['target_position'] == 0)]
    axes[0].scatter(buy_pts['时间'], buy_pts['current_price'], color='red', marker='^', s=40, label='全仓买入')
    axes[0].scatter(sell_pts['时间'], sell_pts['current_price'], color='green', marker='v', s=40, label='空仓卖出')
    axes[0].set_title('交易执行跟踪：真实收盘价轨迹及每次买卖操作点', fontsize=12)
    axes[0].legend(loc='upper right')
    
    # 图2：策略收益率 VS 市场平均收益 (每日累计)
    axes[1].plot(daily_df['日期'], daily_df['策略累计收益率'] * 100, label='策略累计收益率(%)', color='red', marker='o')
    axes[1].plot(daily_df['日期'], daily_df['市场平均累计收益'] * 100, label='市场平均累计收益(%)', color='blue', marker='s')
    axes[1].plot(daily_df['日期'], daily_df['中证500累计收益'] * 100, label='中证500累计收益(%)', color='black', marker='^', alpha=0.85)
    axes[1].set_title('资金双线表现跟踪：累计收益率变化曲线 (%)', fontsize=12)
    axes[1].legend(loc='upper left')
    axes[1].grid(True, linestyle='--')
    
    # 图3：每日最大回撤
    axes[2].fill_between(daily_df['日期'], daily_df['当日最大回撤'] * 100, 0, color='purple', alpha=0.3, label='累计发生最大回撤区域(%)')
    axes[2].plot(daily_df['日期'], daily_df['当日最大回撤'] * 100, color='purple')
    axes[2].invert_yaxis()  # 回撤往下走
    axes[2].set_title('风险控制：日度更新最大回撤 (%)', fontsize=12)
    axes[2].legend(loc='upper right')
    
    # 图4：每日信息比率 IR
    axes[3].bar(daily_df['日期'], daily_df['信息比率(IR)'], color=np.where(daily_df['信息比率(IR)']>0, 'crimson', 'darkgreen'), alpha=0.7)
    axes[3].axhline(0, color='black', linewidth=1)
    axes[3].set_title('主动管理能力评价：每日信息比率 (Information Ratio)', fontsize=12)
    
    plt.tight_layout()
    fig_daily_path = os.path.join(out_dir, f'daily_performance_dashboard_{mode}.png')
    plt.savefig(fig_daily_path, dpi=300)
    plt.close()
    
    mode_text = 'Cheat Mode' if mode == 'cheat' else 'Normal Mode'
    
    print('='*40)
    print(f'🚀 第四问：数字经济板块5分钟频量化回测分析 ({mode_text})')
    print('='*40)
    print(f"🕒 回测区间: {df['时间'].min()} 至 {df['时间'].max()}")
    print(f"💰 初始本金: {initial_capital:,.2f} 元")
    print(f"💎 最终本金: {df['capital'].iloc[-1]:,.2f} 元")
    print('-' * 40)
    print(f'📈 策略总收益率: {total_return * 100:>8.2f}% (市场基准: {market_total_return * 100:.2f}%)')
    print(f'🚀 策略年化收益: {annual_return * 100:>8.2f}%')
    print(f'📉 策略最大回撤: {max_drawdown * 100:>8.2f}%')
    print(f'📊 策略夏普比率: {sharpe_ratio:>8.2f}')
    print('='*40)
    
    out_dir = 'd:/Desktop/Desktop/数学建模/tc_project/outputs/figures'
    os.makedirs(out_dir, exist_ok=True)
    
    plt.figure(figsize=(14, 7))
    curve_label = f'策略资金曲线 (Strategy-{mode_text.split()[0]})'
    plt.plot(df['时间'], df['capital'], label=curve_label, color='#d62728' if mode=='cheat' else '#1f77b4', linewidth=2)
    plt.plot(df['时间'], df['market_capital'], label='完全持仓基准 (Benchmark)', color='#7f7f7f', alpha=0.7, linewidth=1.5)
    plt.plot(df['时间'], df['csi500_capital'], label='中证500基准 (CSI 500)', color='#ff7f0e', alpha=0.85, linewidth=1.6, linestyle='--')
    
    title_text = f'【第四问】100万本金量化投资资金曲线 ({mode_text})'
    plt.title(title_text, fontsize=16, fontweight='bold', pad=15)
    plt.xlabel('交易时间', fontsize=12)
    plt.ylabel('资金账户净值 (人民币/元)', fontsize=12)
    plt.ticklabel_format(style='plain', axis='y')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(fontsize=12, loc='upper left')
    plt.tight_layout()
    
    fig_path = os.path.join(out_dir, f'backtest_equity_curve_{mode}.png')
    plt.savefig(fig_path, dpi=300)
    plt.close()

    # 再给一张超额收益对比图，便于直接证明是否跑赢中证500
    plt.figure(figsize=(14, 6))
    strategy_alpha = df['capital'] / df['csi500_capital'] - 1
    market_alpha = df['market_capital'] / df['csi500_capital'] - 1
    plt.plot(df['时间'], strategy_alpha * 100, label='策略相对中证500超额收益(%)', color='#d62728', linewidth=2)
    plt.plot(df['时间'], market_alpha * 100, label='板块基准相对中证500超额收益(%)', color='#1f77b4', linewidth=1.6)
    plt.axhline(0, color='black', linewidth=1)
    plt.title(f'【第四问】相对中证500的超额收益曲线 ({mode_text})', fontsize=15, fontweight='bold')
    plt.xlabel('交易时间')
    plt.ylabel('相对超额收益(%)')
    plt.legend(loc='upper left')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    alpha_fig_path = os.path.join(out_dir, f'backtest_relative_alpha_{mode}.png')
    plt.savefig(alpha_fig_path, dpi=300)
    plt.close()
    
    out_trade = f'd:/Desktop/Desktop/数学建模/tc_project/outputs/prediction/backtest_trades_{mode}.csv'
    df[['时间', 'prev_price', 'current_price', '预测值', 'expected_return', 'target_position', 'market_return', 'strategy_return', 'csi500_price', 'csi500_return', 'capital', 'csi500_capital', 'strategy_alpha_csi500']].to_csv(out_trade, index=False)
    
    print(f'\n📂 资金曲线图已保存至: {fig_path}')
    print(f'📂 相对中证500超额收益图已保存至: {alpha_fig_path}')
    print(f'📂 交易明细表已保存至: {out_trade}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', type=str, default='normal', choices=['normal', 'cheat'])
    args = parser.parse_args()
    
    if args.mode == 'cheat':
        pred_file = 'd:/Desktop/Desktop/数学建模/tc_project/outputs/prediction/predictions_收盘价_cheat.csv'
    else:
        pred_file = 'd:/Desktop/Desktop/数学建模/tc_project/outputs/prediction/predictions_收盘价.csv'
        
    # 按照赛题(4)要求，传入交易佣金费率 0.3%！
    run_backtest(pred_file, initial_capital=1000000, transaction_cost=0.003, mode=args.mode)

