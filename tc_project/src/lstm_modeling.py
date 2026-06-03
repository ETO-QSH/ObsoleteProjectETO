import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt
import os
import copy
from tqdm import tqdm

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.sans-serif'] = ['SimHei']  
plt.rcParams['axes.unicode_minus'] = False 

class TimeSeriesDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32)
        
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

class DigitalEconomyLSTM(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_layers, output_dim, dropout=0.3):
        super(DigitalEconomyLSTM, self).__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, 
                            batch_first=True, dropout=dropout)
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.LeakyReLU(0.1),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.LeakyReLU(0.1),
            nn.Linear(hidden_dim // 2, output_dim)
        )
        
    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).to(x.device)
        out, _ = self.lstm(x, (h0, c0))
        # Take the output of the last time step
        out = self.fc(out[:, -1, :])
        return out

def create_sequences(data, target, time_steps):
    Xs, ys = [], []
    for i in range(len(data) - time_steps):
        Xs.append(data[i:(i + time_steps)])
        ys.append(target[i + time_steps])
    return np.array(Xs), np.array(ys)

def run_lstm_pipeline(task_name, input_file, target_col, output_dir, time_steps=6, epochs=30, batch_size=64, lr=0.001, volume_mode=None):
    os.makedirs(output_dir, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[{task_name}] Using device: {device}")
    
    # 1. Load Data
    df = pd.read_csv(input_file)
    df['时间'] = pd.to_datetime(df['时间'])
    df = df.sort_values('时间').reset_index(drop=True)
    
    # 【全新特征重构】彻底解决数据缺失引起的 shift(48) 错位错乱导致的“伪波峰”问题
    # 使用日内精确定位，直接告诉模型哪一根K线是当天的开盘，哪一个是收盘
    df['date'] = df['时间'].dt.date
    df['bar_in_day'] = df.groupby('date').cumcount()
    
    # 明确标注极值特征点：打上独热标签
    df['is_open_peak'] = (df['bar_in_day'] == 0).astype(float)    # 09:30 开盘
    df['is_afternoon'] = (df['bar_in_day'] == 24).astype(float)   # 13:00 下午开盘
    df['is_close_peak'] = (df['bar_in_day'] == df.groupby('date')['时间'].transform('count') - 1).astype(float) # 15:00 收盘
    
    df['day_of_week'] = df['时间'].dt.dayofweek
    df.drop(columns=['date'], inplace=True)
    
    # 仅保留短滞后，抛弃非常危险长滞后 target_lag48
    df['target_lag1'] = df[target_col].shift(1)
    
    # 【科学环比：动态同位滚动锚点】(Dynamic Rolling Time-of-Day Anchor)
    # 取代死板的全局半年平均，我们使用严格对齐的具体时间戳（如 9:30），提取它在过去 5 个交易日的均值
    # 这不仅能实现精确的同比/环比，还能完美适应几个月间换手率的冷热周期变化，且完全免疫数据缺失断层
    df['time_str'] = df['时间'].dt.time
    # 分组后，通过移动窗口计算过去5天的同期平均，并严格 shift(1) 避免用到当天未来数据
    df['recent_same_time_mean'] = df.groupby('time_str')[target_col].transform(lambda x: x.rolling(window=5, min_periods=1).mean().shift(1))
    # 对于极少数前几天没有历史均值的数据用回溯填充
    df['recent_same_time_mean'] = df['recent_same_time_mean'].bfill()
    df.drop(columns=['time_str'], inplace=True)
    
    # 构建绝对核心预测变量：
    predict_col = target_col
    if '收盘价' in task_name:
        # 若为收盘价，预测一阶差分
        df['close_diff'] = df[target_col].diff()
        # ======== 第四问模型重训练核心 ========
        # 本次赛题佣金高达 0.3%，微小震荡没有操作空间
        # 对差分建立 EMA 指数平滑（span=6），过滤白噪声，捕捉主升趋势
        df['close_diff'] = df['close_diff'].ewm(span=6, adjust=False).mean()
        predict_col = 'close_diff'
    
    if '成交量' in task_name:
        # 重回全局 Log1p (时间序列不能断！) 
        # 为了解决漂高，主要通过 HuberLoss 以及特征中独热掩码（is_open）让LSTM自己分频。
        df[target_col] = np.log1p(df[target_col])
        df['recent_same_time_mean'] = np.log1p(df['recent_same_time_mean'])
        predict_col = target_col
        
    df = df.dropna().reset_index(drop=True)
    
    # 划分训练集和测试集
    train_mask = (df['时间'] >= '2021-07-14') & (df['时间'] <= '2021-12-31 23:59:59')
    test_mask = (df['时间'] >= '2022-01-04') & (df['时间'] <= '2022-01-28 23:59:59')
    
    feature_cols = [c for c in df.columns if c not in ['时间', target_col, predict_col, 'close_diff']]
    
    # 避免测试集泄露：仅在训练数据上计算标准化参数
    train_df = df[train_mask]
    scaler_x = StandardScaler()
    scaler_y = StandardScaler()
    
    scaler_x.fit(train_df[feature_cols])
    scaler_y.fit(train_df[[predict_col]])
    
    X_scaled = scaler_x.transform(df[feature_cols])
    y_scaled = scaler_y.transform(df[[predict_col]])
    
    # 获取原始目标值作为基准重构用
    target_raw = df[target_col].values
    
    X_seq, y_seq = create_sequences(X_scaled, y_scaled, time_steps)
    _, target_raw_seq = create_sequences(X_scaled, target_raw.reshape(-1, 1), time_steps)
    date_seq = df['时间'].values[time_steps:]
    
    # 按时间切分 sequence
    train_idx = (date_seq >= np.datetime64('2021-07-14')) & (date_seq <= np.datetime64('2021-12-31T23:59:59'))
    test_idx = (date_seq >= np.datetime64('2022-01-04')) & (date_seq <= np.datetime64('2022-01-28T23:59:59'))
    
    # 按照峰值和非峰值进行分离训练 (已废弃：打断了LSTM时序连续性)
    # 这会导致时间序列出现跳跃，使得 LSTM 学习到错误的序列转移 (t -> t+n)。
    # 退回为单体连续训练，采用 HuberLoss 并保留对数操作
    X_train, y_train = X_seq[train_idx], y_seq[train_idx]
    X_test, y_test = X_seq[test_idx], y_seq[test_idx]
    dates_test = date_seq[test_idx]
    
    # 提取测试集的原始价格基准：t-1时刻的真实收盘价
    # 因为 time_steps 序列的最后一步的 target_raw 是 t 时刻，我们要用的是预测出 t 时差分，加上 t-1 时刻的名义物价
    base_price_test = target_raw_seq[test_idx] 
    
    print(f"[{task_name}] Train size: {len(X_train)}, Test size: {len(X_test)}")
    
    train_dataset = TimeSeriesDataset(X_train, y_train)
    test_dataset = TimeSeriesDataset(X_test, y_test)
    
    # 核心调整：训练集启用 shuffle 打乱顺序以打破时序依赖导致的陷入局部最优
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    # 2. Build Model (增加隐藏层宽度)
    input_dim = len(feature_cols)
    model = DigitalEconomyLSTM(input_dim=input_dim, hidden_dim=128, num_layers=2, output_dim=1, dropout=0.3).to(device)
    
    # 【核心调整】再次强调时序连续性，使用 HuberLoss (Smooth L1)
    # L1 Loss 只看中位数，在单模型内容易让峰值拟合彻底放弃；
    # MSE Loss 让非峰值区上飘。
    # Huber Loss 结合了两者的优点，对巨大峰值采用L1边界压制，对小数值采用L2追踪。
    if '成交量' in task_name:
        criterion = nn.HuberLoss(delta=1.0)
    else:
        criterion = nn.MSELoss()
        
    # 增加 weight_decay 防止过拟合
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    # 添加学习率衰减
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    
    # 3. Training Loop
    print(f"[{task_name}] Starting training...")
    best_model_wts = copy.deepcopy(model.state_dict())
    best_loss = np.inf
    
    train_losses = []
    
    for epoch in range(epochs):
        model.train()
        epoch_loss = 0
        for bx, by in train_loader:
            bx, by = bx.to(device), by.to(device)
            optimizer.zero_grad()
            out = model(bx)
            loss = criterion(out, by)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item() * bx.size(0)
            
        epoch_loss /= len(train_loader.dataset)
        train_losses.append(epoch_loss)
        scheduler.step()
        
        if epoch_loss < best_loss:
            best_loss = epoch_loss
            best_model_wts = copy.deepcopy(model.state_dict())
            
        if (epoch+1) % 10 == 0:
            print(f"Epoch {epoch+1}/{epochs} | Loss: {epoch_loss:.6f}")
            
    model.load_state_dict(best_model_wts)
    
    # 4. Evaluation
    model.eval()
    preds = []
    trues = []
    with torch.no_grad():
        for bx, by in test_loader:
            bx = bx.to(device)
            out = model(bx)
            preds.append(out.cpu().numpy())
            trues.append(by.numpy())
            
    preds = np.concatenate(preds, axis=0)
    trues = np.concatenate(trues, axis=0)
    
    # Inverse transform
    preds_inv = scaler_y.inverse_transform(preds).flatten()
    trues_inv = scaler_y.inverse_transform(trues).flatten()
    
    if '收盘价' in task_name:
        # 此时 preds_inv 是预测的“微小涨跌幅(差分)”
        # 真实的收盘价预测值 = t-1 的真实收盘价 + t 的预测涨跌幅
        actual_prev_price = base_price_test.flatten()
        preds_inv = actual_prev_price + preds_inv
        trues_inv = actual_prev_price + trues_inv  # 恢复平移
        
    # 【恢复】针对成交量的 Log1p 的抗变换算，恢复原本的千万级大尺度
    if '成交量' in task_name:
        preds_inv = np.expm1(preds_inv)
        trues_inv = np.expm1(trues_inv)
        
    # Metrics
    mse = mean_squared_error(trues_inv, preds_inv)
    mae = mean_absolute_error(trues_inv, preds_inv)
    # R2
    r2 = r2_score(trues_inv, preds_inv)
    
    print(f"[{task_name}] Test MSE: {mse:.4f} | MAE: {mae:.4f} | R2: {r2:.4f}")
    
    # Save Predictions to CSV
    res_df = pd.DataFrame({'时间': dates_test, '真实值': trues_inv, '预测值': preds_inv})
    res_df.to_csv(os.path.join(output_dir, f'predictions_{task_name}.csv'), index=False)
    
    # Plot Losses
    plt.figure(figsize=(10,4))
    plt.plot(train_losses, label='Train Loss')
    plt.title(f'{task_name} Training Loss')
    plt.xlabel('Epoch')
    plt.ylabel('MSE/L1 Loss')
    plt.legend()
    plt.savefig(os.path.join(output_dir, f'loss_{task_name}.png'), dpi=300)
    plt.close()
    
    return res_df

if __name__ == '__main__':
    vol_input = "d:/Desktop/Desktop/数学建模/tc_project/data/feature/model_data_vol.csv"
    price_input = "d:/Desktop/Desktop/数学建模/tc_project/data/feature/model_data_price.csv"
    out_dir = "d:/Desktop/Desktop/数学建模/tc_project/outputs/prediction"
    
    # 彻底退回：不可在时间序列上过滤断层样本！这会导致时序网络隐藏层丢失依赖。
    # 我们用 Huber Loss 和 额外特征即可让一个完整的序列完美兼容拟合。 
    run_lstm_pipeline('成交量', vol_input, '成交量', out_dir, time_steps=6, epochs=50, lr=0.001)
    
    # 预测收盘价
    run_lstm_pipeline('收盘价', price_input, '收盘价', out_dir, time_steps=6, epochs=50, lr=0.001)
    
    print("All deep learning training finished!")