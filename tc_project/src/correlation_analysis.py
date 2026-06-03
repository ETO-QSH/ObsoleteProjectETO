import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 设置图表风格和中文字体
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.sans-serif'] = ['SimHei']  
plt.rcParams['axes.unicode_minus'] = False 

def correlation_analysis(input_path, output_dir_fig, output_dir_data):
    os.makedirs(output_dir_fig, exist_ok=True)
    os.makedirs(output_dir_data, exist_ok=True)
    
    print("Loading data for correlation analysis...")
    df = pd.read_csv(input_path)
    
    # 过滤掉非数值列
    exclude_cols = ['时间', 'Date', '序号', '指数代码']
    feature_cols = [c for c in df.columns if c not in exclude_cols]
    df_numeric = df[feature_cols].copy()
    
    # 因为存在部分列可能由于异常被识别为 object，安全起见全部转为 float
    for col in df_numeric.columns:
        df_numeric[col] = pd.to_numeric(df_numeric[col], errors='coerce')
        
    df_numeric = df_numeric.fillna(0) # 极少数计算相关系数遭遇Nan会导致结果全Nan，所以补零
    
    # 目标变量
    targets = ['成交量', '收盘价']
    
    # 计算 Pearson 和 Spearman 相关系数
    print("Calculating Pearson correlation...")
    corr_pearson = df_numeric.corr(method='pearson')
    print("Calculating Spearman correlation...")
    corr_spearman = df_numeric.corr(method='spearman')
    
    for target in targets:
        print(f"\nEvaluating target: {target}")
        
        # 获取与 target 的相关性并取绝对值排序
        pearson_target = corr_pearson[target].drop(targets).fillna(0)
        spearman_target = corr_spearman[target].drop(targets).fillna(0)
        
        # 综合考虑绝对值（假设都不服从严格正态分布，主要看 Spearman，辅助看 Pearson）
        corr_summary = pd.DataFrame({
            'Pearson': pearson_target,
            'Spearman': spearman_target,
            'Abs_Spearman': spearman_target.abs()
        }).sort_values(by='Abs_Spearman', ascending=False)
        
        # 保存所有相关性数据表
        corr_summary.to_csv(os.path.join(output_dir_data, f'correlation_{target}.csv'))
        
        # 选择 Top 10 特征画 Heatmap
        top_10_features = corr_summary.head(10).index.tolist()
        plot_cols = [target] + top_10_features
        
        subset_corr = df_numeric[plot_cols].corr(method='spearman')
        
        # 创建简称映射，将长名字转为 Item_1, Item_2...
        short_names = [target] + [f'Item_{i}' for i in range(1, len(top_10_features) + 1)]
        name_mapping = dict(zip(short_names, plot_cols))
        
        # 重命名相关性矩阵的行列为短名称
        subset_corr.index = short_names
        subset_corr.columns = short_names
        
        # 使用 GridSpec 建立 1 行 2 列的图层，左侧放映射表格，右侧放热力图
        fig = plt.figure(figsize=(14, 8))
        gs = fig.add_gridspec(1, 2, width_ratios=[1.2, 3])
        
        ax_text = fig.add_subplot(gs[0])
        ax_heat = fig.add_subplot(gs[1])
        
        # 左侧写入映射文本
        ax_text.axis('off')
        ax_text.text(0, 0.95, "图例：特征名称映射", fontsize=14, fontweight='bold')
        y_pos = 0.88
        for s_name, real_name in name_mapping.items():
            ax_text.text(0, y_pos, f"{s_name} : {real_name}", fontsize=11)
            y_pos -= 0.075
            
        # 绘制热力图
        sns.heatmap(subset_corr, annot=True, fmt=".2f", cmap='coolwarm', 
                    vmin=-1, vmax=1, square=True, linewidths=.5, ax=ax_heat)
        
        # 调整热力图上刻度标签的角度：y轴（左侧）横着，x轴（下侧）斜着
        ax_heat.set_yticklabels(ax_heat.get_yticklabels(), rotation=0)
        ax_heat.set_xticklabels(ax_heat.get_xticklabels(), rotation=45, ha='right')
        
        ax_heat.set_title(f'与 {target} 相关性最强 Top10 (Spearman热力图)', fontsize=14)
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir_fig, f'heatmap_{target}.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
    print("\nCorrelation analysis completed. Figures and data saved.")

if __name__ == '__main__':
    input_file = "d:/Desktop/Desktop/数学建模/tc_project/data/processed/merged_data.csv"
    out_fig = "d:/Desktop/Desktop/数学建模/tc_project/outputs/figures"
    out_data = "d:/Desktop/Desktop/数学建模/tc_project/data/feature"
    
    correlation_analysis(input_file, out_fig, out_data)