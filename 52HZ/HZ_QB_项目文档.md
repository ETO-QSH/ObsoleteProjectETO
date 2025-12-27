<style>
.mermaid {
  display: flex;
  justify-content: center;
}
</style>

<h1 align="center">
  上海港集装箱港区拥堵预测<br>
  <span style="font-size: 0.67em;">
    伪代码 + 流程图 + 说明文字
  </span>
</h1>

> **版本**：v2.0  
> **作者**：ETO-QSH
> **时间**：2025-08-06
> **说明**：本文档面向 2025 年 8 月上海港集装箱港区拥堵预测，采用 “宏观-事件-微观” 三级递进算法，遵循 IMO-FSA、ISO-31000、IALA-G1118 等行业规范。

---

## 目录
1. [项目背景](#项目背景)  
2. [数据资产](#数据资产)  
3. [拥堵定义](#拥堵定义)
4. [总体技术路线](#总体技术路线)  
5. [三级算法详解](#三级算法详解)  
   5.1 L1 宏观长期：Prophet-XGBoost 双残差  
   5.2 L2 事件修正：Bayesian Structural VAR  
   5.3 L3 微观短期：Spatio-Temporal Transformer  
6. [模型融合与置信区间](#模型融合与置信区间)  
7. [结果可视化](#结果可视化)  
8. [行业对标](#行业对标)  
9. [附录](#附录)  

---

## 1. 项目背景
- **痛点**：上海港 2024 年吞吐量 4900 万 TEU，2025 年预计 5050 万 TEU (+3.5 %)。极端天气、关税跳变、北美补货季导致拥堵呈强非线性。  
- **目标**：提前 30 天输出 2025-08 逐小时 **Queue Length (QL)** 与 **Waiting Time (WT)** 概率分布，支撑船公司 ETA 更新、集卡预约、泊位检修排程。  
- **约束**：算法需可解释、可追溯、可复现，并通过 IMO/IALA 合规审查。

---

## 2. 数据资产

| 类别 | 数据 | 粒度 | 时间跨度 | 关键字段 | 更新频率 |
|---|---|---|---|---|---|
| **AIS 动态** | 全球集装箱船报文 | 1 s | 2015-01-01 – 实时 | MMSI, SOG, COG, draught, lon, lat | 流式 |
| **港口作业** | TOS 预约 & 实际靠离 | 1 min | 2015-01-01 – 实时 | 泊位代码, ETA/ATB/ATD, TEU, 桥吊数 | 流式 |
| **集装箱预约** | EDI 报文 | 1 h | 2015-01-01 – 实时 | 提单号, 箱型, 数量, ETA, 船公司 | 1 h |
| **宏观经济** | IMF 全球 GDP、BDI、关税税率 | 月 | 2015-01 – 2025-12 | GDP YoY, BDI, tariff_rate | 月 |
| **季节事件** | 节假日、北美补货旺季 | 事件 | 2015-01 – 2025-12 | 端午、Prime Day、黑五 | 年历 |
| **天气** | ECMWF 高分辨率预报 | 1 h | 2015-01 – 2025-08-31 | 风速、能见度、台风路径 | 6 h |
| **外部冲击** | 运河拥堵、罢工 | 事件 | 2015-01 – 实时 | 苏伊士拥堵天数 | 实时 |

---

## 3. 拥堵定义
| 指标 | 公式 | 轻度拥堵 | 重度拥堵 |
|---|---|---|---|
| **Queue Length QL** | 锚地 + 等待区船舶数 | ≥10 艘 | ≥20 艘 |
| **Waiting Time WT** | 锚地到第一档靠泊 | ≥6 h | ≥12 h |

---

## 4. 总体技术路线

```mermaid
flowchart LR
    A[全量数据湖] -->|Delta Lake| B[Feature Store]
    B --> C[L1 宏观长期<br>Prophet-XGBoost]
    C --> D[日平均 QL 基线]
    D --> E[L2 事件修正<br>Bayesian SVAR]
    E --> F[日级 QL 期望]
    F --> G[L3 微观短期<br>Spatio-Temporal Transformer + DES]
    G --> H[逐小时 QL 分布 & P 拥堵]
    H --> I[可视化 & API]
    I --> J[船公司/集卡/港调]
```

---

## 5. 三级算法详解

### 5.1 L1 宏观长期：Prophet-XGBoost 双残差

#### 5.1.1 目标
预测 2025-08 每日平均 QL。

#### 5.1.2 特征
| 类别 | 变量 | 变换 |
|---|---|---|
| 时间 | 年、月、周、节假日 | Prophet Fourier order=10 |
| 宏观 | IMF 全球 GDP YoY, BDI, tariff_rate | 一阶差分 |
| 港口 | 月度吞吐量, 泊位检修天数 | 标准化 |
| 外部 | 台风频次, 美西拥堵指数 | 累计 |

#### 5.1.3 伪代码
```python
from prophet import Prophet
from xgboost import XGBRegressor
import pandas as pd

# 1. 数据
df = load_monthly()
df['y'] = df['daily_avg_ql']
df['ds'] = df['date']

# 2. Prophet
m = Prophet(yearly_seasonality=10, holidays=china_holidays)
for col in ['gdp_yoy', 'bdi', 'typhoon_cnt']:
    m.add_regressor(col)
m.fit(df)

future = m.make_future_dataframe(periods=31, freq='D')
future.update(load_macro_2025_08())  # 2025-08 宏观
prophet_pred = m.predict(future)['yhat']

# 3. XGBoost 残差
X = df[macro_features]
y_resid = df['y'] - prophet_pred_train
xgb = XGBRegressor(n_estimators=500, max_depth=6, learning_rate=0.03)
xgb.fit(X, y_resid)

resid = xgb.predict(future[macro_features])
daily_ql = prophet_pred + resid
```

#### 5.1.4 验证
- 使用历史数据回测。

---

### 5.2 L2 事件修正：Bayesian Structural VAR

#### 5.2.1 内生向量
$$
\mathbf{Y}_t = [\mathrm{QL}_t, \mathrm{WT}_t, \mathrm{TEU_{in}}_t, \mathrm{TEU_{out}}_t]^T
$$

#### 5.2.2 外生冲击
- 关税跳变：2025-08-15 美线 7.5 %→25 %  
- 台风：ECMWF 25 成员 → 概率加权  
- 端午节假日：dummy=1，乘子 1.35
- 港口罢工 / 航道阻塞：节点移除 / 通路移除

#### 5.2.3 伪代码
```python
import pymc as pm
with pm.Model() as model:
    # Minnesota prior
    beta = pm.Normal('beta', 0, sigma=0.2, shape=(4,4*P))
    Sigma = pm.Wishart('Sigma', nu=4, V=np.eye(4))
    Y_obs = pm.MvNormal('Y_obs', mu=Y_hat, cov=Sigma, observed=Y)
    trace = pm.sample(2000, target_accept=0.9)

# 脉冲响应
irf = pm.stats.impulse_response(model, trace, shocks=event_df)
adj = irf.sum(axis=0)  # 日级调整量
daily_ql *= (1 + adj)
```

---

### 5.3 L3 微观短期：Spatio-Temporal Transformer + 离散事件仿真 (DES)

#### 5.3.1 网络输入
- **空间图**：泊位-锚地拓扑，邻接矩阵 A∈ℝⁿˣⁿ  
- **时间序列**：过去 72 h 特征 → 未来 72 h 逐小时 QL  
- **特征维度**：d_model=256，heads=8，layers=6

#### 5.3.2 Transformer 伪代码
```python
class STTransformer(nn.Module):
    def __init__(self, d_model, n_heads, n_layers):
        super().__init__()
        self.spatial = GATConv(d_model, d_model)
        self.temporal = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(d_model, n_heads), n_layers)
    def forward(self, x, A):
        # x: (T, N, F)
        x = self.spatial(x, A)      # 空间注意力
        x = self.temporal(x)        # 时间注意力
        return x[-72:]              # 未来 72 h

model = STTransformer(...)
train_loader = DataLoader(dataset, batch=64)
trainer = pl.Trainer(gpus=4, max_epochs=200)
trainer.fit(model, train_loader)
```

#### 5.3.3 DES 精细化仿真
```python
import simpy
env = simpy.Environment()
berth = simpy.Resource(env, capacity=52)

def ship_process(env, mmsi, eta, teu):
    yield env.timeout((eta - env.now).seconds/3600)
    if berth.count < berth.capacity:
        with berth.request() as req:
            yield req
            ops_time = np.random.gamma(teu/300, 1.1)
            yield env.timeout(ops_time)
    else:
        queue.append(mmsi)
        yield queue_event
        ...

# 蒙特卡洛 1000 次
for run in range(1000):
    env.run(until=31*24)
hourly_ql_dist = collect_stats()
```

### 5.4 L3-S 多港联动短期修正（Port-Cascade Layer）

#### 5.4.1 场景描述  
- 当宁波-舟山、洋山、外高桥任一港区出现重度拥堵（QL ≥20 艘），船舶将按既定“跳港规则”改靠邻近港区。  
- 跳港概率随拥堵差值、距离、吃水限制动态变化。  

#### 5.4.2 跳港规则表  

| 源港区 | 目标港区 | 距离 (nm) | 吃水限制 (m) | 基准跳港概率 p₀ | 修正因子 |
|---|---|---|---|---|---|
| 宁波-舟山 | 洋山 | 70 | 15.5 | 0.12 | ΔQL/20 |
| 宁波-舟山 | 外高桥 | 120 | 12.5 | 0.08 | ΔQL/20 |
| 洋山 | 外高桥 | 30 | 12.5 | 0.15 | ΔQL/20 |
| 外高桥 | 洋山 | 30 | 15.5 | 0.10 | ΔQL/20 |

ΔQL = 源港区 QL – 目标港区 QL

#### 5.4.3 技术实现  

1. **图构建**：  
   节点 = 港区，边 = 跳港概率，边权实时更新。 

2. **消息传递**：  
   每 5 min 用 **GraphSAGE** 传播拥堵压力：  
   ```python
   class PortGraphSAGE(nn.Module):
       def __init__(self, in_dim, hidden):
           super().__init__()
           self.conv1 = SAGEConv(in_dim, hidden)
           self.conv2 = SAGEConv(hidden, 1)

       def forward(self, x, edge_index, edge_weight):
           x = F.relu(self.conv1(x, edge_index, edge_weight))
           x = self.conv2(x, edge_index, edge_weight)
           return x  # 输出港区拥堵增量
   ```

3. **修正流程**：  
   ```mermaid
   flowchart LR
       A[实时QL] -->|ΔQL| B[跳港概率]
       B --> C[GraphSAGE]
       C --> D[生成新增船舶流]
       D --> E[L3-DES 重跑]
       E --> F[更新上海港QL]
   ```

4. **伪代码**（嵌入 L3-DES 主循环）：  
   ```python
   def cascade_adjust(current_ql):
       """current_ql: dict 港区->QL"""
       edge_index, edge_weight = build_edges(current_ql)
       delta = port_gnn(ql_to_tensor(current_ql), edge_index, edge_weight)
       new_arrivals = poisson(delta['shanghai'])
       for mmsi in range(new_arrivals):
           eta += np.random.exponential(2)  # 2 h 内到达
           env.process(ship_process(env, mmsi, eta, teu=18000))
   ```

---

## 6. 模型融合与置信区间
- **Stacking**：L1、L2、L3 输出 → LightGBM 元学习器  
- **Bootstrap**：1000 次 → 95 % CI  
- **2025-08-15 重度拥堵概率**：  
  - 点估计 34 %  
  - 95 % CI [27 %, 41 %]

---

## 7. 结果可视化

| 图表 | 文件名 | 描述 |
|---|---|---|
| 日历热力图 | `calendar_2025-08.png` | 每日 QL 中位数 |
| 风险曲线 | `risk_curve_0815.png` | 关税生效前后对比 |
| 实时 Dashboard | `dashboard.html` | 交互式，嵌入第一题风险评分 |

<div align="center">
  <img src="./output/calendar_2025-08.png" width="45%" />
  <img src="./output/risk_curve_0815.png" width="45%" />
</div>

---

## 8. 行业对标

| 标准 / 指南 | 条款 | 本项目对应 |
|---|---|---|
| **IMO MSC-Circ.1023** | 步骤 3 风险估计 | 三级量化模型 |
| **ISO 31000** | 风险评估流程 | 风险矩阵 + CI |
| **IALA G1118** | 港口数字孪生 | API 接口规范 |
| **IMF WEO 2025** | 宏观情景 | GDP/贸易量假设 |
| **Clarksons 2025** | 运力供给 | 220 万 TEU 交付 |

---

## 9. 附录

### 9.1 FAQ
- **Q1：为何不用 ARIMA？**  
- A1：季节+外生变量高维，Transformer 更优。  
- **Q2：为何不用单纯 DES？**  
- A2：宏观趋势缺失，需 L1/L2 校正。
- **Q3：为何不像 HZ_QA 一样使用完整的代码建模，而是退化使用伪代码？**  
- A3：尽力了喵呜，啥啥有效数据都薅不到说。我在文档的第一个版本里面是采用和 HZ_QA 一样的项目逻辑，我尝试去收集了一些数据，包括找世界银行、UNCTAD、上海航运交易所、以及其他第三方数据机构，但是由于数据颗粒度不一，数据周期差异较大，无法提供准确的预测环境。同时很多数据都是二级数据，数据分析的结果往往不佳。再者对于短期预测，很多有效数据都是非公开了，我也很难收集到足够的可信的历史样本。一些数据我留在了 external 文件夹下，external/SEARATES/data_reduction.py 是我对爬虫数据进行整理清洗的代码。第一个版本我的思路是使用这些数据进行长期的趋势拟合，再通过爬虫的港口预约数据进行预测，说实话我觉得没什么意义。所以我最后给出了这种预设数据加伪代码的形式，按照 AI 界的说法：在你成事正确按照你成事之后的做法去做，或者说摆了呐 ~
- **Q4：本文对政策因素考虑不足？**  
- A4：航运作为长周期产业，对于大方向的预测固然是比较容易的，但是短期来看受到政策和事件冲击却是非常显著的。尤其近半年，我认为预测这个那家里请高人了……

---

> 联系：2373204754@qq.com
