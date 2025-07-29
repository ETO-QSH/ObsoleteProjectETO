import json
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from sklearn.linear_model import LinearRegression


def read_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def counter_current(data):
    return Counter([item['data']['currentReelResult'] for item in data])


def counter_top_bottom(data):
    return Counter([v for item in data for v in (item['data']['threeSymbols']['top'], item['data']['threeSymbols']['bottom'])])


def counter_reward_level(data):
    return Counter([item['data']['rewardInfo']['level'] for item in data])


def pct_round(pct):
    return f'{int(pct * 10 + 0.5) / 10:.1f}%'


def classify_number(n):
    digits = list(str(n))
    if '0' in digits:
        return ''

    if n == 7777:
        return 'jackpot'

    if len(set(digits)) == 1:
        return 'four_same'

    nums = [int(d) for d in digits]
    if nums == list(range(nums[0], nums[0] + 4)) or nums == list(range(nums[0], nums[0] - 4, -1)):
        return 'straight'

    c = Counter(digits)
    if sorted(c.values()) == [2, 2]:
        return 'two_pairs'

    if sorted(c.values()) == [1, 3]:
        return 'three_same'

    if sorted(c.values()) == [1, 1, 2]:
        return 'one_pair'

    all_odd = all(int(d) % 2 for d in digits)
    all_even = all(int(d) % 2 == 0 for d in digits)
    if (all_odd or all_even) and len(set(digits)) == 4:
        return 'special'

    return 'none'


def build_counter_without_zero():
    counter = Counter()
    for n in range(1111, 10000):
        key = classify_number(n)
        if key:
            counter[key] += 1
    return counter


def plot_two_donuts(counter1, counter2, title1, title2):
    print(counter1, counter2)

    # 按占比降序排序
    items1 = sorted(counter1.items(), key=lambda x: -x[1])
    items2 = sorted(counter2.items(), key=lambda x: -x[1])

    labels1, sizes1 = zip(*items1)
    labels2, sizes2 = zip(*items2)

    # 统一颜色：按字典序给每个标签分配颜色
    all_labels_sorted = sorted(set(labels1) | set(labels2))
    cmap = plt.get_cmap('tab20')

    color_map = {lab: cmap(i / len(all_labels_sorted)) for i, lab in enumerate(all_labels_sorted)}

    colors1 = [color_map[lab] for lab in labels1]
    colors2 = [color_map[lab] for lab in labels2]

    # 画布 1600×900
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 9))
    radius, width = 0.67, 0.33

    # 左侧圆环
    wedges1, _, autotexts1 = ax1.pie(
        sizes1, labels=None, autopct=pct_round, pctdistance=0.5, startangle=90, counterclock=False,
        colors=colors1, wedgeprops=dict(width=width, edgecolor='w')
    )
    ax1.set_title(title1, fontsize=24, fontweight='bold', pad=30)

    # 右侧圆环
    wedges2, _, autotexts2 = ax2.pie(
        sizes2, labels=None, autopct=pct_round, pctdistance=0.5, startangle=90, counterclock=False,
        colors=colors2, wedgeprops=dict(width=width, edgecolor='w')
    )
    ax2.set_title(title2, fontsize=24, fontweight='bold', pad=30)

    # 百分比样式：黑色加粗
    for at in autotexts1 + autotexts2:
        at.set_color('black')
        at.set_weight('bold')
        at.set_fontsize(12)

    # 手工创建图例：颜色、标签一致，单排水平居中
    legend_handles = [patches.Patch(color=color_map[lab], label=lab) for lab in all_labels_sorted]

    fig.legend(
        handles=legend_handles, loc='lower center', bbox_to_anchor=(0.5, 0.01),
        ncol=len(all_labels_sorted), fontsize=16, frameon=False, handletextpad=0.5, columnspacing=2.0
    )

    # 整体布局
    fig.subplots_adjust(top=0.85, bottom=0.15)
    plt.tight_layout(rect=(0.0, 0.05, 1.0, 0.90))
    plt.show()


# ---------- 柱状图 ----------
def plot_bar_chart_log(counter, title):
    """蓝-橘双色并列柱：左=原始频次，右=原始频次×倍率"""
    # 倍率字典
    ratio_map = {
        'one_pair': 72, 'three_same': 672, 'two_pairs': 864, 'special': 1320,
        'straight': 16800, 'four_same': 24000, 'jackpot': 192000, 'none': -20
    }

    # 按原始频次降序
    items = sorted(counter.items(), key=lambda x: -x[1])
    labels, sizes = zip(*items)

    # 计算两列高度（log）
    sizes_log = np.log(sizes)
    sizes_ratio_log = [s * abs(ratio_map.get(lab, 1)) / 5e5 for lab, s in zip(labels, sizes)]

    # 画布
    fig, ax = plt.subplots(figsize=(12, 7.5))
    x = np.arange(len(labels))
    width = 0.4

    # 左蓝右橘
    bars1 = ax.bar(x - width / 2, sizes_log, width=width, color='skyblue', label='原始频次（log）')
    bars2 = ax.bar(x + width / 2, sizes_ratio_log, width=width, color='#ff7f0e', label='计算贡献（K）')

    # 标签
    for b1, b2, s, r in zip(bars1, bars2, sizes, sizes_ratio_log):
        ax.text(
            b1.get_x() + b1.get_width()/2, b1.get_height() + 0.33,
            str(s), ha='center', va='bottom', fontweight='bold', fontsize=13
        )
        ax.text(
            b2.get_x() + b2.get_width()/2, b2.get_height() + 0.33,
            f"{int(s * ratio_map.get(labels[int(b2.get_x() + 0.5)], 1)) / 1000: .1f}".replace('-', '--'),
            ha='center', va='bottom', fontweight='bold', fontsize=13
        )

    # y 轴
    ax.set_ylim(0, 15)
    ax.set_title(title, fontsize=16, fontweight='bold', pad=25)
    ax.tick_params(axis='y', labelsize=12)
    ax.legend(fontsize=12)

    # 右轴：橘色柱
    ax2 = ax.twinx()
    ax2.set_ylim(0, 7.5)
    ax2.tick_params(axis='y', labelsize=12)

    # x 轴文字向下
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=0)
    for label in ax.get_xticklabels():
        label.set_fontsize(15)
        label.set_verticalalignment('top')
        label.set_y(-0.03)

    # 居中
    fig.subplots_adjust(top=0.88, bottom=0.12)
    plt.tight_layout(rect=(0, 0.05, 1, 0.95))
    plt.show()


def plot_balance_trend(data):
    """
    连线折线 + 最小二乘直线（x 为连续索引）
    """
    # 按时间升序
    ts_bal = [(item['data']['gameStartTs'], item['data']['newBalance']) for item in data]
    ts_bal.sort(key=lambda x: x[0])
    _, balance = zip(*ts_bal)

    # x 用连续索引
    x_idx = np.arange(len(balance)).reshape(-1, 1)
    y = np.array(balance)

    # 直线拟合
    reg = LinearRegression().fit(x_idx, y)
    y_line = reg.predict(x_idx)

    # 绘图
    fig, ax = plt.subplots(figsize=(12, 7.5))
    # 直线
    ax.plot(x_idx, y_line, color='red', linewidth=2, label=f'Fit: y={reg.coef_[0]:.2f}x+{reg.intercept_:.2f}')
    # 连线折线
    ax.plot(x_idx, balance, color='steelblue', linewidth=2, label='Balance')

    # 美观
    ax.set_title('Balance Trend & Least-Squares Fit', fontsize=16, fontweight='bold', pad=25)
    ax.set_xlabel('Sequence Index', fontsize=14)
    ax.set_ylabel('New Balance', fontsize=14)
    ax.tick_params(axis='both', labelsize=12)
    ax.grid(alpha=0.3)
    ax.legend()
    plt.tight_layout()
    plt.show()


# ---------- 主程序 ----------
if __name__ == '__main__':
    data = [d for d in read_json('database.json') if d['code'] == 0]
    plt.rcParams['font.sans-serif'] = ['Lolita']
    print(build_counter_without_zero())

    plot_two_donuts(
        counter_current(data), counter_top_bottom(data),
        'Current Reel Result Frequency', 'Top and Bottom Symbol Frequency'
    )

    plot_bar_chart_log(
        counter_reward_level(data),
        'Reward Level Frequency'
    )

    plot_balance_trend(data)
