import pandas as pd
import numpy as np
import xgboost as xgb
import os

def feature_engineering_and_selection(input_file, output_dir):
    print("Loading preprocessed data...")
    df = pd.read_csv(input_file)
    df['时间'] = pd.to_datetime(df['时间'])
    df = df.sort_values('时间').reset_index(drop=True)
    
    # 构建基础的高频滞后特征 (利用过去自身的特征)
    # 对于 5分钟预测，加入拉后的开、高、低、收、量等
    for lag in [1, 2, 3]:
        df[f'收盘价_lag{lag}'] = df['收盘价'].shift(lag)
        df[f'成交量_lag{lag}'] = df['成交量'].shift(lag)
    
    # 填补滞后产生的缺失值
    df = df.bfill()
    
    # 分割数据集
    # 按照题目规定：2021年7月14日至2021年12月31日为训练集
    train_mask = (df['时间'] >= '2021-07-14') & (df['时间'] < '2022-01-01')
    df_train = df[train_mask].copy()
    
    # 被选择作为特征的列（排除目标本身和时间列以及非数值列）
    target_vol = '成交量'
    target_price = '收盘价'
    exclude_cols = ['时间', '开盘价', '最高价', '最低价', '成交额', target_vol, target_price]
    features = [c for c in df.columns if c not in exclude_cols and pd.api.types.is_numeric_dtype(df[c])]
    
    print(f"Total candidate features: {len(features)}")
    
    # 我们为“成交量”做一个XGBoost特征筛选
    X_train = df_train[features]
    y_train_vol = df_train[target_vol]
    y_train_price = df_train[target_price]
    
    # 特征筛选模型 1：针对成交量的预测
    print("Training XGBoost for Volume to get feature importance...")
    model_vol = xgb.XGBRegressor(
        n_estimators=100, 
        max_depth=5, 
        learning_rate=0.1, 
        n_jobs=-1,
        random_state=42
    )
    model_vol.fit(X_train, y_train_vol)
    
    # 提取特征重要性
    imp_vol = pd.DataFrame({'Feature': features, 'Importance_Vol': model_vol.feature_importances_})
    imp_vol = imp_vol.sort_values(by='Importance_Vol', ascending=False)
    
    # 特征筛选模型 2：针对收盘价的预测
    print("Training XGBoost for Close Price to get feature importance...")
    model_price = xgb.XGBRegressor(
        n_estimators=100, 
        max_depth=5, 
        learning_rate=0.1, 
        n_jobs=-1,
        random_state=42
    )
    model_price.fit(X_train, y_train_price)
    
    imp_price = pd.DataFrame({'Feature': features, 'Importance_Price': model_price.feature_importances_})
    imp_price = imp_price.sort_values(by='Importance_Price', ascending=False)
    
    # 保存特征重要性结果
    os.makedirs(output_dir, exist_ok=True)
    imp_vol.to_csv(os.path.join(output_dir, 'feature_importance_vol.csv'), index=False)
    imp_price.to_csv(os.path.join(output_dir, 'feature_importance_price.csv'), index=False)
    
    # 选择Top 20特征组成精简后的特征数据集，用于后续模型
    top20_vol = imp_vol.head(20)['Feature'].tolist()
    top20_price = imp_price.head(20)['Feature'].tolist()
    
    # 我们保留特征列 + 目标列 + 时间列 导出新的数据集
    selected_cols_vol = ['时间', target_vol] + top20_vol
    selected_cols_price = ['时间', target_price] + top20_price
    
    df[selected_cols_vol].to_csv(os.path.join(output_dir, 'model_data_vol.csv'), index=False)
    df[selected_cols_price].to_csv(os.path.join(output_dir, 'model_data_price.csv'), index=False)
    
    print("Feature selection completed!")
    print(f"Top 5 features for Volume: {top20_vol[:5]}")
    print(f"Top 5 features for Price: {top20_price[:5]}")

if __name__ == "__main__":
    feature_engineering_and_selection(
        input_file="d:/Desktop/Desktop/数学建模/tc_project/data/processed/merged_data.csv",
        output_dir="d:/Desktop/Desktop/数学建模/tc_project/data/feature"
    )