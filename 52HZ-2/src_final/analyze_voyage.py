"""航行日志贡献分析"""
import sys; sys.path.insert(0,str(__import__('pathlib').Path(__file__).parent.parent/"src_final"))
import pandas as pd, numpy as np
from pathlib import Path

ROOT=Path(__file__).parent.parent; OUTPUT=ROOT/"output_final"

# 加载航行日志
vl=pd.read_parquet(ROOT/"database"/"voyage_log.parquet")
vl['mmsi']=pd.to_numeric(vl['mmsi'],errors='coerce')
vl=vl.dropna(subset=['mmsi'])
vl['mmsi']=vl['mmsi'].astype(int)

# 每船统计
stats=vl.groupby('mmsi').agg(
    recorded_calls=('Event_id','count'),
    unique_ports=('nowPortName','nunique'),
    months=('Begin_time',lambda x: max((x.max()-x.min()).days/30,1)),
    avg_duration=('End_time',lambda x: (x-vl.loc[x.index,'Begin_time']).mean()),
).reset_index()
stats['calls_per_month']=(stats['recorded_calls']/stats['months']).round(1)
print(f"航行日志覆盖: {len(stats)} 艘")
print(stats.head())

# 合并 vessel_risk_profile
vp=pd.read_csv(OUTPUT/"vessel_risk_profile.csv")
vp['mmsi']=vp['mmsi'].astype(int)
merged=vp.merge(stats,on='mmsi',how='left')
merged['calls_per_month']=merged['calls_per_month'].fillna(0)

# 对比: 有日志 vs 无日志
has_log=merged['calls_per_month']>0
print(f"\n有航行日志: {has_log.sum()} 艘, 无: {(~has_log).sum()} 艘")
for label, mask in [('有日志',has_log),('无日志',~has_log)]:
    sub=merged[mask]
    sanc=(sub['sanction_sources'].fillna(0)>0).sum()
    print(f"  {label}: logistic={sub['logistic_score'].mean():.1f} sanction={sanc}/{len(sub)} port_interval={sub['port_interval'].mean():.3f}")

# 相关性
cols=['calls_per_month','logistic_score','port_interval','port_dwell','sanction_sources']
corr=merged[cols].corr()['calls_per_month'].drop('calls_per_month')
print(f"\n与calls_per_month相关性:")
print(corr.to_string())

# 能不能作为特征?
print(f"\ncalls_per_month std={merged['calls_per_month'].std():.3f} (需>{0.01}才有区分力)")
