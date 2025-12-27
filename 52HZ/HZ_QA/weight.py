import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from sklearn.preprocessing import MinMaxScaler


def entropy_weight_2h(ind: pd.DataFrame) -> pd.Series:
    """
    面向海事通道安全的熵权法
    1. 极值标准化（0-1）
    2. 信息熵 e_j = - Σ p_ij ln p_ij / ln(n)
    3. 差异系数 d_j = 1 - e_j
    4. 权重 w_j = d_j / Σ d_k
    返回：权重 Series
    """
    cols = ['rho', 'C', 'speed', 'ΔM']
    if len(ind) < 2:
        return pd.Series([0.25] * len(cols), index=cols)  # 等权兜底

    # 极值标准化（正向指标） + 防 NaN
    scaler = MinMaxScaler()
    X = scaler.fit_transform(ind[cols].astype(float))
    X = np.nan_to_num(X, nan=0.0)

    # 比重矩阵
    col_sum = X.sum(axis=0)
    col_sum = np.where(col_sum == 0, 1, col_sum)  # 防 0
    p = X / col_sum

    # 信息熵
    n = len(ind)
    e = -(1 / np.log(n)) * (p * np.log(p + 1e-12)).sum(axis=0)

    # 差异系数 & 熵权
    d = 1 - e
    w = d / d.sum()
    return pd.Series(w, index=cols)


def risk_score_2h(ind: pd.DataFrame, w: pd.Series) -> pd.DataFrame:
    """
    通道级 2h 安全评分
    输入：DataFrame 每行 2h 桶 + 4 指标
    输出：含原始列 + 综合评分 R ∈ [0,1]
    公式：R_i = Σ w_j · r_ij
    """
    ind = ind.copy()

    # 先标准化再加权
    scaler = MinMaxScaler()
    X = scaler.fit_transform(ind[w.index].astype(float))
    X = np.nan_to_num(X, nan=0.0)

    ind['R'] = pd.DataFrame(X, columns=w.index).dot(w)
    ind['start'] = ind['interval'].str.split('-').str[0].astype(int)

    ind = ind.sort_values('start').drop(columns=['start'])
    return ind[['interval', 'rho', 'C', 'speed', 'ΔM', 'R']]


def plot_2h_risk(data, out_path: str) -> None:
    """
    支持两种输入：
    1. DataFrame
    2. CSV 文件路径
    输出：单图 PNG
    """
    # 中文字体（我喜欢这个说）
    plt.rcParams['font.sans-serif'] = ['Lolita']
    plt.rcParams.update({'font.size': 15, 'axes.titlesize': 18})

    # 统一读入
    ind = pd.read_csv(data) if isinstance(data, str) else data.copy()

    # 排序区间
    ind['start'] = ind['interval'].str.split('-').str[0].astype(int)
    ind = ind.sort_values('start').drop(columns=['start'])

    # 标准化
    cols = ['rho', 'C', 'speed', 'ΔM', 'R']
    scaler = pd.DataFrame(ind[cols]).apply(lambda x: (x - x.min()) / (x.max() - x.min()))

    # 绘图
    fig, ax = plt.subplots(figsize=(16, 9))
    ind['xlabel'] = ind['interval'].str.replace('-', '--')
    [ax.plot(ind['xlabel'], scaler[c], marker='o', label=c) for c in ['rho', 'C', 'speed', 'ΔM']]

    ax.bar(ind['xlabel'], scaler['R'], alpha=0.33, color='red', label='R')
    ax.set_title(' '.join(i for i in '通道级 2h 风险（标准化）'), pad=30, loc='center')
    ax.legend(
        loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=len(cols),
        frameon=False, handletextpad=0.5, columnspacing=5
    )

    plt.tight_layout(rect=(0.02, 0.00, 0.97, 0.97))
    plt.savefig(out_path)
    plt.close()
