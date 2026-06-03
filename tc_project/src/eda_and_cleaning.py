import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 设置绘图风格与中文字体（Windows自带SimHei）
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.sans-serif'] = ['SimHei']  
plt.rcParams['axes.unicode_minus'] = False 

def eda_and_cleaning(raw_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    print("Loading core target data for EDA...")
    xls = pd.ExcelFile(raw_path)
    
    # 获取数字经济板块 5 分钟数据
    df = pd.read_excel(xls, sheet_name='数字经济版块信息')
    df = df[~df['时间'].isin(['频率', '单位'])].copy()
    
    # 将时间转化为 datetime，如果转化失败会得到 NaT
    df['时间'] = pd.to_datetime(df['时间'], errors='coerce')
    
    # 强制数值类型
    numeric_cols = ['开盘价', '收盘价', '最高价', '最低价', '成交量', '成交额']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 1. 缺失值分析与处理
    total_len = len(df)
    missing_info = df.isnull().sum()
    print("--- 缺失值统计 ---")
    print(missing_info)
    
    # 缺失值可视化 (条形图)
    plt.figure(figsize=(10, 6))
    sns.barplot(x=missing_info.index, y=missing_info.values, palette='viridis')
    plt.title('原始数据各字段缺失值统计 (Missing Values Check)', fontsize=14)
    plt.ylabel('缺失数量', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'missing_values_bar.png'), dpi=300)
    plt.close()
    
    # 执行缺失值填充（前向填充）并剔除前置仍有缺失的（比如首行）
    df_cleaned = df.copy()
    df_cleaned = df_cleaned.ffill().bfill()
    
    # 2. 重复值分析与处理
    dup_count = df_cleaned.duplicated(subset=['时间']).sum()
    print(f"\n--- 重复值统计 ---\n基于时间的重复记录数: {dup_count}")
    # 剔除重复值，保留第一条
    if dup_count > 0:
        df_cleaned = df_cleaned.drop_duplicates(subset=['时间'], keep='first')
        
    # 3. 异常值分析 (3-Sigma 准则)
    # 取 成交量 和 收盘价 作为示例指标
    def detect_outliers_3sigma(data, col):
        mean = data[col].mean()
        std = data[col].std()
        lower_bound = mean - 3 * std
        upper_bound = mean + 3 * std
        outliers = data[(data[col] < lower_bound) | (data[col] > upper_bound)]
        return outliers, lower_bound, upper_bound
        
    outliers_vol, low_v, up_v = detect_outliers_3sigma(df_cleaned, '成交量')
    outliers_price, low_p, up_p = detect_outliers_3sigma(df_cleaned, '收盘价')
    
    print(f"\n--- 异常值统计 (3-Sigma) ---")
    print(f"成交量 异常值数量: {len(outliers_vol)} (下界:{low_v:.2f}, 上界:{up_v:.2f})")
    print(f"收盘价 异常值数量: {len(outliers_price)} (下界:{low_p:.2f}, 上界:{up_p:.2f})")
    
    # 绘制箱线图体现异常值分布 (处理前 vs 处理后可视化展示，我们只做截断展示)
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    sns.boxplot(y=df_cleaned['成交量'], ax=axes[0], color='skyblue')
    axes[0].set_title('成交量箱线图及异常值分布', fontsize=12)
    
    sns.boxplot(y=df_cleaned['收盘价'], ax=axes[1], color='lightcoral')
    axes[1].set_title('收盘价箱线图及异常值分布', fontsize=12)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'outliers_boxplot.png'), dpi=300)
    plt.close()
    
    # 异常值处理：这里我们在时序数据中常采用“截断法(Winsorization)”以防止数据截断产生时间断层
    df_cleaned['成交量'] = np.clip(df_cleaned['成交量'], low_v, up_v)
    df_cleaned['收盘价'] = np.clip(df_cleaned['收盘价'], low_p, up_p)
    
    # 4. 时序趋势总览
    plt.figure(figsize=(15, 6))
    plt.plot(df_cleaned['时间'], df_cleaned['收盘价'], label='收盘价', color='red', alpha=0.8)
    plt.title('数字经济板块5分钟收盘价走势图', fontsize=14)
    plt.xlabel('时间')
    plt.ylabel('价格')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'price_trend.png'), dpi=300)
    plt.close()
    
    print("\nEDA and Cleaning visualizations generated in outputs/figures/")

if __name__ == '__main__':
    raw_path = "d:/Desktop/Desktop/数学建模/tc_project/data/raw/database.xlsx"
    out_dir = "d:/Desktop/Desktop/数学建模/tc_project/outputs/figures"
    eda_and_cleaning(raw_path, out_dir)