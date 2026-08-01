"""
航行日志处理: RAR → 过滤676 MMSI → Parquet
"""
import sys; sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent.parent/"src_final"))
import rarfile, pandas as pd, pyarrow as pa, pyarrow.parquet as pq
from pathlib import Path
from datalib_final import get_all_mmsi

ROOT=Path(__file__).parent.parent
RAR_DIR=ROOT/"决赛资料"/"航行日志"
CACHE=ROOT/"database"; CACHE.mkdir(exist_ok=True)
PARQUET_OUT=CACHE/"voyage_log.parquet"
rarfile.UNRAR_TOOL=r"D:\Program Files\WinRAR\UnRAR.exe"

# 获取676个MMSI
our_mmsi=set(get_all_mmsi())
print(f"目标MMSI: {len(our_mmsi)}")

COLS=["Event_id","mmsi","Mmsi_cate","Ship_name","IMO",
      "Begin_time","End_time","Begin_lon","Begin_lat","end_lon","end_lat",
      "Middle_lon","Middle_lat","Avg_lon","Avg_lat",
      "Middle_hdg","Max_hdg","Min_hdg","Middle_sog","Max_sog",
      "Middle_cog","Max_cog","Min_cog","Max_rot","Min_rot","Middle_rot",
      "Point_num","avgSpeed","AvgSteadySpeed","SailingDist",
      "Zone_id","Navistate","nowPortName","nowPortId","nowDockName","nowDockId",
      "nowBerthName","nowBerthId","nowPortLon","nowPortLat",
      "Event_categories","province","Country","Event_cate"]

DTYPES={c:"str" for c in COLS}
for c in ["Begin_time","End_time","Begin_lon","Begin_lat","end_lon","end_lat",
          "Middle_lon","Middle_lat","Avg_lon","Avg_lat","nowPortLon","nowPortLat",
          "Middle_hdg","Max_hdg","Min_hdg","Middle_sog","Max_sog","Middle_cog","Max_cog","Min_cog",
          "Max_rot","Min_rot","Middle_rot","Point_num","Navistate","Event_cate","Zone_id"]:
    DTYPES[c]="float64"

rars=sorted(RAR_DIR.glob("*.rar"))
print(f"RAR文件: {len(rars)}")

total=0; writer=None
for rp in rars:
    print(f"\n解压: {rp.name}")
    rf=rarfile.RarFile(rp)
    for fn in rf.namelist():
        if not fn.endswith('.csv'): continue
        print(f"  读取: {fn}")
        f=rf.open(fn)
        try:
            chunk=pd.read_csv(f,header=0,names=COLS,dtype=DTYPES,low_memory=False,on_bad_lines='skip')
        except:
            chunk=pd.read_csv(f,header=0,names=COLS,low_memory=False,on_bad_lines='skip')
        f.close()
        
        # 过滤MMSI
        before=len(chunk)
        chunk=chunk[chunk['mmsi'].astype(str).str.strip().apply(
            lambda x: int(float(x)) if x.replace('.','',1).replace('-','',1).isdigit() else 0).isin(our_mmsi)]
        if len(chunk)==0:
            print(f"    过滤后0行, 跳过")
            continue
        print(f"    保留: {len(chunk)}/{before}")
        
        # 坐标转换
        for c in ["Begin_lon","Begin_lat","end_lon","end_lat","Middle_lon","Middle_lat","Avg_lon","Avg_lat","nowPortLon","nowPortLat"]:
            if c in chunk.columns:
                chunk[c]=pd.to_numeric(chunk[c],errors='coerce')/1_000_000
        
        # 时间转换
        for c in ["Begin_time","End_time"]:
            if c in chunk.columns:
                chunk[c]=pd.to_datetime(pd.to_numeric(chunk[c],errors='coerce'),unit='s',utc=True)
        
        table=pa.Table.from_pandas(chunk)
        if writer is None:
            writer=pq.ParquetWriter(PARQUET_OUT,table.schema,compression='zstd')
        writer.write_table(table)
        total+=len(chunk)
        del chunk,table
    rf.close()

if writer: writer.close()
print(f"\n完成: {total}行 → {PARQUET_OUT} ({PARQUET_OUT.stat().st_size/1024**2:.0f}MB)")
print(f"唯一MMSI: {len(pq.ParquetFile(PARQUET_OUT).schema.names)}")
