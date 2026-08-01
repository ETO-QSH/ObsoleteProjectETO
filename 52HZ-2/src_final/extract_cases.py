"""提取四艘候选船的完整AIS轨迹"""
import pyarrow.parquet as pq, pandas as pd
from pathlib import Path

ROOT=Path(r'D:\Desktop\Desktop\海事')
PARQUET=ROOT/'database'/'ais_clean_2026.parquet'
OUT=ROOT/'output_final'/'case_study'
OUT.mkdir(parents=True,exist_ok=True)

ships={273251810:'Ligovsky_Prospect', 667002070:'Kousai', 613961020:'Aqua_Titan', 273279840:'Nasledie'}

for mmsi,name in ships.items():
    tbl=pq.read_table(str(PARQUET),filters=[('mmsi','=',mmsi)])
    df=tbl.to_pandas()
    df.to_csv(OUT/f'{name}.csv',index=False)
    print(f'{name}: {len(df):,} points, {df["acqtime"].min()} ~ {df["acqtime"].max()}')
