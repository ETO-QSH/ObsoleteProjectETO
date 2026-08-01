# 52Hz AIS 数据处理库

> 船舶 AIS（自动识别系统）动态轨迹数据与静态信息处理

---

## 项目概述

本项目处理 `2025 年 3-4 月 && 2026 年 3-4 月` 的船舶 AIS 数据，包含：
- **动态数据**：约 8.14 亿条轨迹记录（按日切片）
- **静态数据**：约 302 万条船舶静态信息（按月切片，已清洗）
- **船舶档案**：LNG 船和油轮档案数据

所有原始 RAR/CSV 已清理，数据以 Parquet 格式缓存于 `./database`。

⚠️ **重要**：运行环境容器内存限制为 **2GB**，必须通过 API 按需读取，禁止全量加载。

---

## 数据文件

| 文件 | 路径 | 大小      | 行数            | 列数 |
|------|------|---------|---------------|------|
| 动态数据 | `./database/ais_dynamic_25.parquet` | 17.1 GB | 814,064,125   | 21 |
| 动态数据 | `./database/ais_dynamic_26.parquet` | 22.2 GB | 1,071,535,234 | 21 |
| 静态数据 | `./database/ais_static.parquet` | 25.8 MB | 1,520,629     | 18 |
| 船舶档案 | `./database/ship_archive.parquet` | 1.86 MB | 18,591        | 42 |

---

## 数据结构

### 1. 动态数据（ais_dynamic.parquet）

时间范围：**2025-03-01 ~ 2025-04-30 | 2026-03-01 ~ 2026-04-30**

| 列名 | 类型 | 说明 | 单位/备注 |
|------|------|------|----------|
| `mmsi` | int64 | MMSI 编号 | 9 位数字 |
| `acqtime` | timestamp[ns, UTC] | 采集时间 | UTC，秒级 Unix 时间戳解析 |
| `target_type` | int8 | 目标类型 | 0=船舶, 1=车辆, 2=吊机 |
| `data_supplier` | int8 | 数据供应商 | 0-255 |
| `data_source` | int8 | 数据来源 | 0=基站, 1=卫星, 2=车载, 3=码头 |
| `move_status` | int8 | 航行状态 | 0=在航, 1=锚泊, 2=失控, ... |
| `longitude` | float64 | 经度 | 已 ÷1e6，东=+，西=- |
| `latitude` | float64 | 纬度 | 已 ÷1e6，北=+，南=- |
| `area_id` | int64 | 位置 ID | 0.001×0.001 粒度 |
| `speed` | int16 | 原始速度 | 1/10 节 |
| `conversion` | float32 | 转换系数 | 0.514444（节→m/s） |
| `cog` | int16 | 原始对地航向 | 1/100 度 |
| `heading` | int16 | 原始船首向 | 1/100 度 |
| `power` | float32 | 功率 | 千瓦 |
| `imitator` | string | 套牌标注 | A/B/C...，正常为空 |
| `extend` | string | 扩展信息 | Rot&Pos_acc&... |
| `speed_knots` | float64 | 速度 | 节（已转换） |
| `speed_ms` | float64 | 速度 | 米/秒（已转换） |
| `cog_deg` | float64 | 对地航向 | 度（已转换） |
| `heading_deg` | float64 | 船首向 | 度（已转换） |
| `date` | timestamp[ns] | 日期 | 对应 CSV 文件名中的日期 |

### 2. 静态数据（ais_static.parquet）

时间范围：**2025-03-01 ~ 2025-04-30 | 2026-03-01 ~ 2026-04-30**

原始约 619 万行（3 个月 CSV 合计），清洗后约 152 万行。

**清洗规则：**
- MMSI 必须为 9 位纯数字，否则丢弃（过滤 731,152 条）
- 列名标准化：`shipname`→`ship_name`, `shiptype`→`ship_type`, `breadth`→`width`
- 删除 pandas 索引列 `Unnamed: 0`
- 去重：同 MMSI 保留 month 最大者；同 month 按 eta 保留最新
- `""` / `"nan"` / `"None"` 等脏数据转为 `NaN`/`NaT`

| 列名 | 类型 | 说明 | 备注 |
|------|------|------|------|
| `mmsi` | int64 | MMSI 编号 | 9 位数字，主键 |
| `imo` | string | IMO 号 | 可能为空 |
| `callsign` | string | 船舶呼号 | 可能为空 |
| `ship_name` | string | 船舶英文名 | 可能为空 |
| `ship_type` | Int64 | 船舶类型 | 可空整数，见下表 |
| `length` | float64 | 船长 | 米 |
| `width` | float64 | 船宽 | 米 |
| `pos_fixing_device` | Int64 | 定位设备 | 可空整数，可忽略 |
| `eta` | string | 预抵港时间 | 月-日 时:分 |
| `draught` | float64 | 吃水深度 | 毫米 |
| `destination` | string | 目的地 | 船员填写，可能错填 |
| `classtype` | string | 设备类型 | A/B |
| `receivetime` | datetime64[ns, UTC] | 收到时间 | UTC，兼容 Unix 时间戳和 ISO 字符串 |
| `to_bow` | Int64 | 天线到船首 | 米，可空 |
| `to_stern` | Int64 | 天线到船尾 | 米，可空 |
| `to_port` | Int64 | 天线到左舷 | 米，可空 |
| `to_starboard` | Int64 | 天线到右舷 | 米，可空 |
| `month` | string | 数据月份 | 202503 / 202504 / 202603 |

**船舶类型对照表：**

| 代码 | 类型 |
|------|------|
| 30 | 捕捞 |
| 31-32 | 拖引 |
| 33-35 | 疏浚/潜水/军事 |
| 36 | 帆船 |
| 37 | 娱乐船 |
| 50-59 | 引航/搜救/拖轮/供应/执法/医疗 |
| 60-69 | 客船 |
| 70-79 | 货船 |
| 80-89 | 油轮 |
| 90-99 | 其他 |

### 3. 船舶档案（ship_archive.parquet）

| 列名 | 类型 | 说明 |
|------|------|------|
| `archive_type` | string | 档案类型：LNG / Tanker |
| `ship_id` | int64 | 船舶 ID |
| `ship_name` | string | 船舶名称 |
| `ship_imo` | string | IMO 号 |
| `ship_mmsi` | string | MMSI 号 |
| `ship_build_year` | int64 | 建造年份 |
| `ship_type_id` | int64 | 船舶类型 ID |
| `ship_type` | string | 船舶类型 |
| `ship_status` | string | 船舶状态 |
| `ship_country_name` | string | 船旗国名称 |
| `leg_shape` | string | 船型 |
| `scrubber_type_name` | string | 脱硫塔类型名称 |
| `scrubber_name` | string | 脱硫塔名称 |
| `ship_scrubber_fit_date` | string | 脱硫塔安装日期 |
| `offshore_equipment_maker_name` | string | 海上设备制造商 |
| `ship_size` | float64 | 船舶吨位 |
| `ship_type_name` | string | 船舶类型名称 |
| `ship_country_id` | int64 | 船旗国 ID |
| `build_year` | int64 | 建造年份（备用） |
| `ship_alt_size` | float64 | 替代吨位 |
| `ship_dead` | float64 | 载重吨 |
| `ship_builder_id` | int64 | 造船厂 ID |
| `ship_builder_type` | string | 造船厂类型 |
| `ship_builder_name` | string | 造船厂名称 |
| `ship_builder_region` | string | 造船厂地区 |
| `ship_builder_parent_id` | int64 | 造船厂母公司 ID |
| `ship_builder_ownership` | string | 造船厂所有权 |
| `ship_builder_alternative` | string | 造船厂别名 |
| `ship_builder_url` | string | 造船厂 URL |
| `ship_builder_country_id` | int64 | 造船厂国家 ID |
| `ship_builder_country_name` | string | 造船厂国家名称 |
| `operator_id` | int64 | 运营商 ID |
| `operator_name` | string | 运营商名称 |
| `operator_country_id` | int64 | 运营商国家 ID |
| `operator_country` | string | 运营商国家 |
| `operator_country_flag_position` | string | 运营商国旗位置 |
| `size_metric` | string | 吨位计量单位 |
| `size_metric_alt` | string | 替代吨位计量单位 |
| `ship_href` | string | 船舶详情链接 |
| `operator_url` | string | 运营商 URL |
| `ship_country_flag_position` | string | 船旗国国旗位置 |
| `ship_builder_country_flag_position` | string | 造船厂国家国旗位置 |

---

## 使用方法

```python
from datalib import get_ais_dynamic, get_ais_static, get_ship_archive

# ========== 动态数据（必须带过滤，默认 limit=10万）==========

# 按日期范围 + 指定列
df = get_ais_dynamic(
    date_start="2025-03-01",
    date_end="2025-03-05",
    columns=["mmsi", "acqtime", "longitude", "latitude", "speed_knots"],
    limit=100_000
)

# 按 MMSI 列表
df = get_ais_dynamic(mmsi_list=[412123456, 413456789], limit=10_000)

# 按地理范围（bbox: min_lon, min_lat, max_lon, max_lat）
df = get_ais_dynamic(
    bbox=(120.0, 30.0, 122.0, 32.0),  # 上海附近
    limit=50_000
)

# 迭代器模式（大数据量，逐批处理）
for gdf in get_ais_dynamic_iter(date_start="2025-03-01", date_end="2025-03-01"):
    process(gdf)  # 每批约 10 万行

# ========== 静态数据（按 MMSI 查询）==========

static = get_ais_static()  # 返回 StaticData 对象，不加载全量

# 查询单条
record = static.get_by_mmsi(412549105)  # 返回 pd.Series 或 None

# 批量查询
df = static.get_by_mmsi_list([412549105, 355328000])

# 逐批迭代
for batch in static.iter_batches(batch_size=100_000):
    process(batch)

# ========== 船舶档案 ==========

archive = get_ship_archive()  # 返回 pd.DataFrame
```

---

## 环境要求

```bash
pip install pandas pyarrow geopandas rarfile
# 系统依赖
apt-get install -y unrar
```

---

## 注意事项

1. **内存限制**：容器 cgroup 内存限制为 **2GB**，`pd.read_parquet` 全量加载 8 亿行会直接 OOM Kill。必须使用 `get_ais_dynamic()` 的过滤参数或迭代器模式。

2. **时间戳**：`acqtime` 和 `receivetime` 原始为 **秒级 Unix 时间戳**，已转换为 UTC datetime。

3. **坐标转换**：原始经纬度单位为 **1/1000000 度**，已除以 1e6 转换为标准经纬度。

4. **速度转换**：原始速度单位为 **1/10 节**，已转换为 `speed_knots`（节）和 `speed_ms`（米/秒）。

5. **静态数据清洗**：原始静态数据存在 `""` 空字符串和错误 MMSI，已清洗：
   - MMSI 必须为 9 位纯数字，否则丢弃
   - `""` 转为 `None`/`NaN`
   - 原始 570 万行 → 清洗后 302 万行

6. **缓存位置**：所有 Parquet 缓存位于 `/root/autodl-tmp/52hz_cache/`，代码目录（`~/52hz/`）仅保留脚本，不存数据。

7. **原始数据已清理**：RAR 分卷和原始 CSV 已删除，仅保留 Parquet 缓存。

---

## 文件清单

```
52hz/
├── datalib.py              # 数据加载库（核心）
└── database/
    ├── ais_dynamic_25.parquet
    ├── ais_dynamic_26.parquet
    ├── ais_static.parquet
    └── ship_archive.parquet
```
