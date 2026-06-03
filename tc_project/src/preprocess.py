import pandas as pd
import numpy as np
import os

def load_and_preprocess(input_path, output_dir):
    print("Loading data...")
    xls = pd.ExcelFile(input_path)
    
    # 1. 加载5分钟高频数据（锚点）
    df_5min = pd.read_excel(xls, sheet_name='数字经济版块信息')
    # 处理第一两行可能是单位和频率的问题
    # 观察发现行预览里第一行没有单位，是正常的OHLC数据。等一下，我们需要清理一下
    # pandas 如果遇到表头有"单位"会导致列类型变成 object。
    
    # 我们先看看前几行是不是正常的
    print("5min shape:", df_5min.shape)
    # 处理时间列
    df_5min = df_5min[~df_5min['时间'].isin(['频率', '单位'])].copy()
    df_5min['时间'] = pd.to_datetime(df_5min['时间'], errors='coerce')
    df_5min = df_5min.dropna(subset=['时间'])
    df_5min = df_5min.sort_values('时间').reset_index(drop=True)
    df_5min['Date'] = df_5min['时间'].dt.date
    
    # 2. 读取并处理其他日、月、季频表
    def process_low_freq(sheet_name, time_col='指标名称'):
        df = pd.read_excel(xls, sheet_name=sheet_name)
        # 清理异常行（频率、单位，以及来源说明等）
        df = df[~df[time_col].isin(['频率', '单位'])].copy()
        
        # 将无法转换的值转为NaT，并直接将这些行删除
        df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
        df = df.dropna(subset=[time_col])
        
        df = df.rename(columns={time_col: 'Date'})
        df['Date'] = df['Date'].dt.date
        df = df.sort_values('Date').reset_index(drop=True)
        # 将非日期列转换为数值型
        for col in df.columns:
            if col != 'Date' and col != '序号' and col != '指数代码':
                df[col] = pd.to_numeric(df[col], errors='coerce')
        return df

    # 日频
    df_tech = process_low_freq('技术指标', '时间')
    df_dom = process_low_freq('国内市场指标')
    df_int = process_low_freq('国际市场指标')
    df_fx = process_low_freq('汇率')
    df_other = process_low_freq('其他板块信息', '日期')

    # 宏观（月/季频）
    df_macro1 = process_low_freq('宏观市场指标1')
    df_macro2 = process_low_freq('宏观市场指标2')
    
    print("Merging features...")
    # 对低频数据（月度、季度），我们需要先构建一个完整的日历日历频，用ffill
    # 获取所有的日期范围
    all_dates = pd.date_range(start=df_5min['Date'].min(), end=df_5min['Date'].max(), freq='D').date
    df_calendar = pd.DataFrame({'Date': all_dates})
    
    # 合并宏观数据到日历并ffill (因为宏观数据变动慢)
    df_macro = pd.merge(df_calendar, df_macro1, on='Date', how='left')
    df_macro = pd.merge(df_macro, df_macro2, on='Date', how='left')
    df_macro = df_macro.infer_objects(copy=False).ffill().bfill()  # 填充缺失
    
    # 合并日频特征
    # 严格来说，使用当天的日频特征预测当天的日内5分钟可能涉及未来数据(看收盘)，
    # 但为了对齐，常态下题目允许使用同日指标。我们为了严谨将日频统一按日期 left join。
    # 也对日频数据中的周末NaN进行一定的前向填充
    df_daily = pd.merge(df_calendar, df_tech, on='Date', how='left')
    df_daily = pd.merge(df_daily, df_dom, on='Date', how='left')
    df_daily = pd.merge(df_daily, df_int, on='Date', how='left')
    df_daily = pd.merge(df_daily, df_fx, on='Date', how='left')
    df_daily = pd.merge(df_daily, df_other, on='Date', how='left', suffixes=('', '_other'))
    
    # 移除重复列并前移填充 (ffill) 来处理非交易日或缺失
    df_daily = df_daily.infer_objects(copy=False).ffill().bfill()
    
    # 合并日级别和宏观级别的所有低频特征
    daily_features = pd.merge(df_daily, df_macro, on='Date', how='left')
    
    # 为了避免未来函数（即当天的日线特征在当天 10:00 是未知的），我们把所有日频特征 shift(1)
    # 这样 merge 到 5 分钟线就使用的是昨天的收盘后特征
    # [依据比赛严谨度要求] 但若某些指标如汇率或国内市场开盘前指标可见则无需。安全起见，shift(1)。
    daily_features_shifted = daily_features.copy()
    feature_cols = [c for c in daily_features.columns if c not in ['Date', '序号', '指数代码']]
    daily_features_shifted[feature_cols] = daily_features_shifted[feature_cols].shift(1)
    
    # 为了填补第一天的nan，bfill一下
    daily_features_shifted = daily_features_shifted.bfill()
    
    # 将汇总后的低频特征合并到高频5分钟数据
    df_final = pd.merge(df_5min, daily_features_shifted, on='Date', how='left')
    df_final.drop(columns=['Date', '序号', '指数代码', '序号_other', '指数代码_other'], inplace=True, errors='ignore')
    
    # 把目标相关的全部转成 float
    for col in ['开盘价', '收盘价', '最高价', '最低价', '成交量', '成交额']:
        df_final[col] = pd.to_numeric(df_final[col], errors='coerce')
        
    df_final = df_final.ffill().bfill()
    
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'merged_data.csv')
    df_final.to_csv(output_file, index=False)
    print(f"Data preprocessing done. Saved to {output_file}. Shape: {df_final.shape}")

if __name__ == "__main__":
    load_and_preprocess(
        input_path="d:/Desktop/Desktop/数学建模/tc_project/data/raw/database.xlsx",
        output_dir="d:/Desktop/Desktop/数学建模/tc_project/data/processed"
    )