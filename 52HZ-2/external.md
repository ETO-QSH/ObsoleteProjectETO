# External 外源数据说明

## 1. 数据概述

本目录用于存放项目中除 AIS 原始数据之外的外部辅助数据。

外源数据主要用于：

- 构建海事空间分析环境
- 定义关键航运区域
- 关联全球港口与贸易网络
- 分析霍尔木兹海峡事件对能源运输、贸易流和航运市场的影响
- 对 AIS 轨迹分析结果进行验证和经济背景解释

数据来源包括：

- 美国能源信息署（EIA, U.S. Energy Information Administration）
- 国际货币基金组织（IMF）
- 世界银行（World Bank）
- 国际贸易与发展组织（UNCTAD）
- 世界银行 PortWatch 平台
- World EEZ 数据集
- 历史项目数据整理
- STOCKQ 航运指数平台

目录结构：

```
external/
├── EIA/
├── IMF/
├── PORTWATCH/
├── SISI/
├── STOCKQ/
├── UNCTAD/
└── WORLDEEZ/
```

---

## 2. EIA 能源数据

**路径**：`external/EIA/`

**来源**：美国能源信息署（U.S. Energy Information Administration）

**官网**：https://www.eia.gov/

### 2.1 数据内容

包含全球能源市场相关时间序列：

```
EIA/data/
├── Brent_daily.csv          (381 行, 11 列)
├── WTI_daily.csv            (374 行, 11 列)
├── HenryHub_daily.csv       (372 行, 11 列)
├── CrudeExport_weekly.csv   (79 行, 11 列)
├── CrudeProduction_weekly.csv (79 行, 11 列)
└── RefineryInput_weekly.csv (79 行, 11 列)
```

### 2.2 数据说明

所有 EIA CSV 文件采用统一的 11 列结构：

| 列名 | 说明 |
|------|------|
| `period` | 日期 |
| `duoarea` | 地区代码 |
| `area-name` | 地区名称 |
| `product` | 产品代码 |
| `product-name` | 产品名称 |
| `process` | 处理类型代码 |
| `process-name` | 处理类型名称 |
| `series` | 序列代码 |
| `series-description` | 序列描述 |
| `value` | 数值 |
| `units` | 单位 |

#### Brent 原油价格

**文件**：`Brent_daily.csv`

**内容**：北海 Brent 原油日价格。`period` 为日期，`value` 为价格（$/BBL），`series-description` 为 "Europe Brent Spot Price FOB"。

**用途**：

- 分析霍尔木兹事件对国际油价影响
- 与 AIS 油轮流量变化进行时间关联
- 分析能源市场风险变化

#### WTI 原油价格

**文件**：`WTI_daily.csv`

**内容**：美国西德克萨斯轻质原油价格，`series-description` 为 "Cushing, OK WTI Spot Price FOB"。

**用途**：

- 对比全球主要原油价格变化
- 分析能源市场波动

#### Henry Hub 天然气价格

**文件**：`HenryHub_daily.csv`

**内容**：美国天然气基准价格，`series-description` 为 "Henry Hub Natural Gas Spot Price"。

**用途**：

- 分析 LNG 市场变化
- 与 LNG 船舶运输变化关联

#### 原油出口量

**文件**：`CrudeExport_weekly.csv`

**内容**：美国原油出口变化，`process-name` 为 "Ending Stocks Excluding SPR"。

**用途**：

- 分析能源供应替代来源
- 研究霍尔木兹封锁后的供应链调整

#### 原油产量

**文件**：`CrudeProduction_weekly.csv`

**内容**：美国原油产量，`process-name` 为 "Field Production"。

**用途**：分析全球能源供应端变化。

#### 炼厂输入量

**文件**：`RefineryInput_weekly.csv`

**内容**：美国炼厂净输入量，`process-name` 为 "Refinery Net Input"。

**用途**：分析炼化需求变化。

---

## 3. IMF / World Bank 数据

**路径**：`external/IMF/`

**来源**：

- 国际货币基金组织（IMF）
- 世界银行（World Bank）

### 3.1 数据内容

包含：`World Bank Commodity Price Data.xlsx`

世界主要商品价格数据库，主要包括：

- 原油
- 天然气
- 煤炭
- 金属等

### 3.2 用途

用于：

- 宏观经济背景分析
- 能源价格趋势分析
- 航运变化的经济解释

**例如**：

- AIS 显示霍尔木兹油轮减少
- 结合原油价格上涨
- 分析能源供应风险

---

## 4. PORTWATCH 港口监测数据

**路径**：`external/PORTWATCH/`

**来源**：世界银行 PortWatch 平台

**官网**：https://portwatch.imf.org/

### 4.1 数据内容

PortWatch 提供全球主要港口和海峡的船舶活动监测。

#### 海峡通行数据

**路径**：`PORTWATCH/Calls/Channel/`

包括：

- Bab el-Mandeb Strait
- Cape of Good Hope
- Malacca Strait
- Strait of Hormuz
- Suez Canal

每个海峡包含两个子目录：

```
Transit Calls/
  └── arrivals-of-ships.csv    (2,743 行, 8 列)
Transit Trade Volume/
  └── chart.csv                (2,743 行, 8 列)
```

**列名**（8 列）：

| 列名 | 说明 |
|------|------|
| `DateTime` | 日期时间 |
| `Container` | 集装箱船 |
| `Dry Bulk` | 干散货船 |
| `General Cargo` | 杂货船 |
| `Roll-on/roll-off` | 滚装船 |
| `Tanker` | 油轮 |
| `7-day Moving Average` | 7 日移动平均 |
| `Prior Year: 7-day Moving Average` | 去年同期 7 日移动平均 |

#### 国家运输数据

**路径**：`PORTWATCH/Calls/National/`

包括：

- China
- India
- Iraq
- Japan
- Kuwait
- Qatar
- Saudi Arabia
- South Korea
- The Netherlands
- United Arab Emirates
- United States

每个国家包含三个子目录：

```
Incoming Shipment/
  └── incoming-shipment.csv    (2,741 行, 8 列)
Outgoing Shipment/
  └── outgoing-shipment.csv    (2,741 行, 8 列)
Port Calls/
  └── arrivals-of-ships.csv    (2,741 行, 8 列)
```

**列名**（8 列）：

| 列名 | 说明 |
|------|------|
| `DateTime` | 日期时间 |
| `Container` | 集装箱船 |
| `Dry Bulk` | 干散货船 |
| `General Cargo` | 杂货船 |
| `Roll-on/roll-off` | 滚装船 |
| `Tanker` | 油轮 |
| `30-day Moving Average` | 30 日移动平均 |
| `Prior Year: 30-day Moving Average` | 去年同期 30 日移动平均 |

#### 港口数据

**路径**：`PORTWATCH/Ports/`

包含：

- `Ports.csv` (2,065 行, 25 列)
- `Ports.geojson` (2,065 个要素, 23 个属性列)
- `PortWatch_ports_database.zip` (含 Shapefile 格式)

**Ports.csv 字段**（25 列）：

| 列名 | 说明 |
|------|------|
| `X` | Web Mercator X 坐标 |
| `Y` | Web Mercator Y 坐标 |
| `portid` | 港口 ID |
| `portname` | 港口名称 |
| `country` | 国家 |
| `ISO3` | ISO3 国家代码 |
| `continent` | 大洲 |
| `fullname` | 完整名称 |
| `lat` | 纬度 |
| `lon` | 经度 |
| `vessel_count_total` | 船舶总数 |
| `vessel_count_container` | 集装箱船数 |
| `vessel_count_dry_bulk` | 干散货船数 |
| `vessel_count_general_cargo` | 杂货船数 |
| `vessel_count_RoRo` | 滚装船数 |
| `vessel_count_tanker` | 油轮数 |
| `industry_top1` | 第一大产业 |
| `industry_top2` | 第二大产业 |
| `industry_top3` | 第三大产业 |
| `share_country_maritime_import` | 国家海运进口份额 |
| `share_country_maritime_export` | 国家海运出口份额 |
| `LOCODE` | 港口代码 |
| `pageid` | 页面 ID |
| `countrynoaccents` | 无重音国家名 |
| `ObjectId` | 对象 ID |

#### 区域运输数据

**路径**：`PORTWATCH/Calls/Region/`

包括：

- Emerging and Developing Asia
- European Union
- Middle East and Central Asia

以及 `PORTWATCH/Calls/World/` 全球汇总数据。

结构与国家数据相同，包含 Incoming Shipment、Outgoing Shipment、Port Calls。

#### 贸易监测数据

**路径**：`PORTWATCH/Monitor/`

包含 TRADE VALUE 和 TRADE VOLUME 两个子目录，各含：

- World Export Value (77 行, 2 列: DateTime, 3-month MA)
- World Import Value (77 行, 2 列)
- World Trade Value (77 行, 2 列)

#### 地缘政治紧张度数据

**路径**：`PORTWATCH/Tension/`

包括：

- China
- European Union
- United States
- World

每个包含 Incoming Shipment、Outgoing Shipment、Port Calls（或 Shipment），均为 2,376 行，2 列（DateTime, 30-day Moving Average）。

### 4.2 PortWatch 数据用途

#### AIS 结果验证

**例如**：

- AIS 分析：霍尔木兹船舶数量下降 40%
- PortWatch：Hormuz Transit Calls 下降
- 两者互相验证

#### 全球贸易变化分析

用于研究：港口活动 → 贸易流 → 供应链变化

---

## 5. SISI 航运市场数据

**路径**：`external/SISI/`

**来源**：历史海事研究数据整理

**主要用于**：油运市场分析

### 5.1 原油贸易数据

**路径**：`1、原油贸易、成品油贸易数据/`

包含：

- `China_Refinery.csv` (119 行, 6 列)
  - `Date`, `Crude_Imp`（原油进口）, `PG_Imp`（成品油进口）, `PG_Exp`（成品油出口）, `PG_NetImp`（成品油净进口）, `Total_Feed`（总加工量）
- `中国进口原油海运量_2025-10-17.xls`
- `中国进口成品油海运量_2025-10-17.xls`
- `中国出口成品油海运量_2025-10-17.xls`

**用途**：

- 分析能源贸易方向
- 分析亚洲能源供应变化

### 5.2 全球油轮贸易流

**路径**：`2、航运与船队数据，全球油轮船队构成与货流数据/`

包含：

- `country_flow_analysis_with_pct.csv` (86 行, 7 列)
  - `国家`, `出口量`, `出口占比(%)`, `进口量`, `进口占比(%)`, `净流量`, `角色`
- `crude_oil_flow.json` — 2022-2024 年原油国别贸易流数据
- `油轮船舶档案.csv` (20,417 行, 10 列)
  - `Name`, `Vessel type`, `MMSI`, `IMO`, `Beneficial Owner`, `Registered Owner`, `Class`, `Builder`, `Operator`, `Technical Manager`
- `2022-2024原油全球货流分析.xlsx`
- `2022-2024内贸成品油货流分析.xlsx`

**用途**：构建产油国 → 运输通道 → 消费国贸易网络

### 5.3 运价指数

**路径**：`3、油运市场上中、欧航线相关分航线、分船型的价格指数或价格/`

包含：

- `BDTI_Monthly_Avg.csv` (120 行, 2 列: 日期, BDTI)
- `BDTI_AllRoutes_Weighted.csv` (36 行, 12 列)
  - `日期`, `TD3C`, `TD9`, `TD7`, `TD8`, `TD15`, `TD1`, `TD6`, `中国加权`, `欧洲加权`, `中国加权 线性`, `欧洲加权 线性`
- `CTFI_Monthly_Avg.csv` (60 行, 5 列)
  - `日期`, `中东湾拉斯坦努拉—中国宁波`, `西非马隆格/杰诺—中国宁波`, `加权平均`, `线性拟合`
- `BDTI分航线运价指数（日）_2025-10-17.xls`
- `中国进口原油运价指数_2025-10-17.xls`
- `海上丝绸之路进口原油运价指数(分航线)_2025-10-17.xls`

**用途**：分析风险增加 → 航线改变 → 运输成本上涨

### 5.4 油轮轨迹历史数据

**路径**：`4、MR型成品油轮、阿芙拉型成品油轮、VLCC油轮，2020年-2024年，每年1-3月的船舶轨迹数据/`

包含：

- `output/heatmap_cartopy_2020.png`
- `test_output/test_rgb_2020~2024.png` — 5 年热力图
- `background_map.png`
- `heatmap.py`, `datalib.py`, `background_map.py` 等脚本

**用途**：

- 参考油轮航线模式
- 验证轨迹分析方法

### 5.5 主要油轮船型市场价格

**路径**：`5、主要油轮船型的市场价格/`

包含：

- `Newbuilding_Price_and_UnitPrice.csv` (585 行, 4 列)
  - `年月`, `船型`（VLCC/苏伊士型/巴拿马型）, `价格`, `单位价格`
- `Ship_Depreciation_Rate_Monthly.csv` (1,404 行, 4 列)
  - `年月`, `船型`, `船龄`, `折旧率`
- `Tanker_Price_Index_Monthly.csv` (117 行, 3 列)
  - `日期`, `二手指数`, `新指数`
- `VLCC二手售价（周）_2025-10-17.xls`
- `二手油船价格指数_2025-10-17.xls`
- `二手船价格_2025-10-17.xls`
- `新油船价格指数_2025-10-17.xls`
- `新船价格_2025-10-17.xls`

**用途**：分析油轮市场资产价值变化

---

## 6. STOCKQ 航运指数数据

**路径**：`external/STOCKQ/`

**来源**：STOCKQ 航运指数平台

### 6.1 Baltic Dirty Tanker Index（波罗的海原油运价指数）

**文件**：`Baltic Dirty Tanker index.png`

**内容**：BDTI 指数价格走势图，时间跨度约两年（2024 年 9 月至 2026 年 7 月），包含 Price（日价格）、MA20（20 日移动平均）、MA60（60 日移动平均）、MA120（120 日移动平均）四条曲线。

**数据特征**：

| 指标 | 说明 |
|------|------|
| 时间跨度 | 约 2024.09 ~ 2026.07（两年） |
| 纵轴范围 | 0 ~ 4,000 点 |
| 曲线 | Price（蓝色）、MA20（红色）、MA60（橙色）、MA120（绿色） |

**走势特征**：

- **2024 年 9 月 ~ 2025 年底**：指数在 800~1,200 点区间低位震荡，MA 各周期均线粘合，市场处于平淡期
- **2026 年初**：指数开始快速攀升，从约 1,200 点突破至 3,000 点以上
- **2026 年 3 月**：达到峰值约 3,700 点，为两年内最高点
- **2026 年 4~5 月**：高位回落，MA20 下穿 MA60，形成死叉
- **2026 年 6~7 月**：继续下行，MA60 与 MA120 趋于粘合，价格回落至 2,000 点附近

**与项目关联**：

- 2026 年初的 BDTI 暴涨与霍尔木兹海峡事件高度时间重合
- 可用于验证 AIS 分析中油轮绕航导致的运价上涨假设
- 结合 SISI 的 BDTI 分航线数据，可进一步分析中国航线与欧洲航线的涨幅差异

**用途**：

- 验证 AIS 油轮绕航对运价的影响
- 分析霍尔木兹事件前后油运市场波动
- 与 EIA 能源价格数据联动，分析"能源供应风险 → 运价上涨"传导链条

---

## 7. UNCTAD 数据

**路径**：`external/UNCTAD/`

**来源**：联合国贸易和发展会议（UNCTAD）

### 数据内容

**Global Trade Update**（全球贸易更新报告）：

- `Global_Trade_Update_March_2026.pdf`
- `Global_Trade_Update_April_2026.pdf`
- `Global_Trade_Update_May_2026.pdf`
- `Global_Trade_Update_June_2026.pdf`

**Strait of Hormuz Disruptions**（霍尔木兹海峡中断专题报告）：

- `Strait_of_Hormuz_Disruptions_March_2026.pdf`
- `Strait_of_Hormuz_Disruptions_April_2026.pdf`
- `Strait_of_Hormuz_Disruptions_May_2026.pdf`
- `Strait_of_Hormuz_Disruptions_June_2026.pdf`

**其他报告**：

- `Trade_and_Development_Foresights_2026.pdf`
- `World_economic_situation_and_prospects_as_of_mid_2026.pdf`

### 用途

用于：

- 提供事件背景
- 支撑研究结论
- 分析全球供应链影响

**例如**：解释为什么油轮改变航线、为什么运价上涨

---

## 8. WORLDEEZ 海洋空间数据

**路径**：`external/WORLDEEZ/`

**来源**：World EEZ v12

### 8.1 世界专属经济区数据

**文件**：`World_EEZ_v12_20231025.zip`

**内容**：全球国家海洋管辖区域，包含 Shapefile 格式：

```
World_EEZ_v12_20231025/
├── eez_v12.shp          (163.9 MB)
├── eez_v12.dbf
├── eez_v12.shx
├── eez_boundaries_v12.shp (14.2 MB)
└── ...
```

**用途**：判断 AIS 位置属于哪个国家海域。

**例如**：

- AIS 点 → 空间匹配 → Iran EEZ / Oman EEZ / Saudi EEZ

### 8.2 关键航运区域

**路径**：`WORLDEEZ/corridor/`

包含：

- `Strait_of_Hormuz.geojson`
- `Strait_of_Malacca.geojson`
- `Cape_of_Good_Hope.geojson`
- `Suez_Canal.geojson`

**GeoJSON 属性列**（31 列）：

| 列名 | 说明 |
|------|------|
| `MRGID` | 海洋区域 ID |
| `GEONAME` | 区域名称 |
| `MRGID_TER1` | 领土 1 ID |
| `POL_TYPE` | 多边形类型（200NM / Overlapping claim） |
| `MRGID_SOV1` | 主权国 1 ID |
| `TERRITORY1` | 领土 1 名称 |
| `ISO_TER1` | 领土 1 ISO 代码 |
| `SOVEREIGN1` | 主权国 1 名称 |
| `MRGID_TER2` ~ `SOVEREIGN3` | 领土 2/3 信息（重叠区域） |
| `X_1`, `Y_1` | 中心坐标 |
| `MRGID_EEZ` | EEZ ID |
| `AREA_KM2` | 面积（平方公里） |
| `ISO_SOV1` ~ `ISO_SOV3` | 主权国 ISO 代码 |
| `UN_SOV1` ~ `UN_TER3` | UN 代码 |

#### 用途

用于空间过滤：

**例如**：

- **霍尔木兹海峡**：Point in Polygon → 船舶数量
- **波斯湾**：进入数量 / 离开数量
- **红海**：绕航分析

---

## 9. 外源数据与 AIS 数据结合关系

整体分析流程：

```
           AIS 动态数据
                |
                |
        船舶轨迹分析
                |
    --------------------------------
    |              |               |
 空间区域分析    港口分析        船型分析
    |              |               |
 WORLDEEZ      PORTWATCH      船舶档案
    |              |               |
    |              |               |
 航线变化        流量变化        船型变化
    |              |               |
    |              |               |
 EIA 能源价格  SISI/STOCKQ    UNCTAD 报告
    |          运价数据           |
    --------------------------------
                |
          综合影响分析
```

---

## 10. 数据用途总结

| 数据源 | 主要用途 |
|--------|----------|
| EIA | 能源价格、供应变化分析 |
| IMF/World Bank | 宏观贸易和商品价格背景 |
| PORTWATCH | 港口和海峡活动验证 |
| SISI | 油运市场和贸易流分析 |
| STOCKQ | 实时运价指数走势验证 |
| UNCTAD | 事件背景和全球贸易解释 |
| WORLDEEZ | 海洋空间分析、区域划分 |

---

## 11. 数据使用说明

所有外源数据主要用于：

1. AIS 轨迹空间分析辅助
2. 霍尔木兹海峡影响评估
3. 全球能源运输网络分析
4. 航运市场变化解释
5. 研究结果交叉验证

外源数据不直接替代 AIS 分析结果，而作为：

- 空间约束
- 背景信息
- 经济指标
- 独立验证数据

共同支撑最终分析结论。
