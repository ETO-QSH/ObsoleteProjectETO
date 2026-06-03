import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.sans-serif'] = ['SimHei']  
plt.rcParams['axes.unicode_minus'] = False 

def comprehensive_indicator_selection(feature_dir, output_dir_fig):
    os.makedirs(output_dir_fig, exist_ok=True)
    
    # 1. 加载相关性结果与 XGBoost 特征重要性结果
    corr_vol = pd.read_csv(os.path.join(feature_dir, 'correlation_成交量.csv'), index_col=0)
    corr_price = pd.read_csv(os.path.join(feature_dir, 'correlation_收盘价.csv'), index_col=0)
    
    xgb_vol = pd.read_csv(os.path.join(feature_dir, 'feature_importance_vol.csv')).set_index('Feature')
    xgb_price = pd.read_csv(os.path.join(feature_dir, 'feature_importance_price.csv')).set_index('Feature')
    
    # 2. 合并并对齐特征池 (剔除我们人造的 lag1, lag2 等时序衍生特征，以及原本表格里带有的噪声如“序号”)
    exclusion_list = ['成交量', '收盘价', '开盘价', '最高价', '最低价', '成交额', '序号_x', '序号_y', '序号']
    indicators = [idx for idx in corr_vol.index if 'lag' not in idx and idx not in exclusion_list]
    
    df_scores = pd.DataFrame(index=indicators)
    df_scores['Spearman_Vol'] = corr_vol.loc[indicators, 'Abs_Spearman']
    df_scores['Spearman_Price'] = corr_price.loc[indicators, 'Abs_Spearman']
    
    # XGBoost的重要度中如果存在某些指标缺失用 0 填充
    df_scores['XGB_Vol'] = xgb_vol['Importance_Vol'].reindex(indicators).fillna(0)
    df_scores['XGB_Price'] = xgb_price['Importance_Price'].reindex(indicators).fillna(0)
    
    # 3. 归一化 (Min-Max Scaling) 以便统一量纲计算综合得分
    for col in df_scores.columns:
        min_v, max_v = df_scores[col].min(), df_scores[col].max()
        if max_v - min_v > 0:
            df_scores[f'{col}_norm'] = (df_scores[col] - min_v) / (max_v - min_v)
        else:
            df_scores[f'{col}_norm'] = 0.0
            
    # 4. 构建综合评价模型 (CRITIC思想或简单等权加权)
    # 综合考量：成交量和收盘价的驱动因素同样重要；线性和非线性同样重要
    df_scores['综合重要度得分'] = (
        0.25 * df_scores['Spearman_Vol_norm'] +
        0.25 * df_scores['Spearman_Price_norm'] +
        0.25 * df_scores['XGB_Vol_norm'] +
        0.25 * df_scores['XGB_Price_norm']
    )
    
    df_scores = df_scores.sort_values(by='综合重要度得分', ascending=False)
    
    # 保存结果表用于附录或详细分析
    df_scores.to_csv(os.path.join(feature_dir, '综合特征筛选得分表_Question1.csv'))
    
    # 5. 提取 Top 15 绘制综合条形图
    top_n = 15
    top_indicators = df_scores.head(top_n)
    
    plt.figure(figsize=(12, 8))
    sns.barplot(x='综合重要度得分', y=top_indicators.index, data=top_indicators, palette='magma')
    plt.title('第一问提取核心结论：“数字经济”板块关联度最高的核心指标 Top15', fontsize=16)
    plt.xlabel('综合关联重要度评分 (XGBoost与Spearman交叉测算)', fontsize=12)
    plt.ylabel('原始提供指标名称', fontsize=12)
    plt.tight_layout()
    
    fig_path = os.path.join(output_dir_fig, 'Question1_Top_Indicators.png')
    plt.savefig(fig_path, dpi=300)
    plt.close()
    
    print("Question 1 integration completed!")
    print(f"Top 5 indicators overall: {top_indicators.index[:5].tolist()}")
    print(f"File saved to {fig_path}")

if __name__ == '__main__':
    data_dir = "d:/Desktop/Desktop/数学建模/tc_project/data/feature"
    fig_dir = "d:/Desktop/Desktop/数学建模/tc_project/outputs/figures"
    comprehensive_indicator_selection(data_dir, fig_dir)