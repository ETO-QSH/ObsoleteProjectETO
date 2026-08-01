"""v3指标 + 制裁港口 (含CI)"""
import sys; sys.path.insert(0,str(__import__('pathlib').Path(__file__).parent.parent/"src_final"))
import pandas as pd,numpy as np,pyarrow.parquet as pq,geopandas as gpd,time
from pathlib import Path
from shapely.geometry import Point as ShpPt; from shapely import prepared
ROOT=Path(__file__).parent.parent; OUTPUT=ROOT/"output_final"
PARQUET=ROOT/"database"/"ais_clean_2026.parquet"
PORTS=ROOT/"决赛资料"/"原油装卸港清单"/"原油装卸港清单_详细.csv"

def wilson(s,n,z=1.96):
    if n==0:return 0.0,0.0,0.0
    p=s/n; z2=z*z; c=(p+z2/(2*n))/(1+z2/n)
    m=z/(1+z2/n)*np.sqrt(p*(1-p)/n+z2/(4*n*n))
    return round(max(0.0,c-m),6),round(min(1.0,c+m),6),round(c,6)

def fisher(r,n,z=1.96):
    if r>=1.0:r=0.9999
    if r<=-1.0:r=-0.9999
    if n<4:return -1.0,1.0,r
    zf=0.5*np.log((1+r)/(1-r)); se=1.0/np.sqrt(n-3)
    lo=zf-z*se; hi=zf+z*se
    return round((np.exp(2*lo)-1)/(np.exp(2*lo)+1),4),round((np.exp(2*hi)-1)/(np.exp(2*hi)+1),4),round(r,4)

def main():
    t0=time.time()
    pdf=pd.read_csv(PORTS)
    pdf=pdf[pdf['lat'].notna()&(pdf['lat']!='')]
    pdf['lat']=pd.to_numeric(pdf['lat'],errors='coerce'); pdf['lon']=pd.to_numeric(pdf['lon'],errors='coerce')
    pdf=pdf.dropna(subset=['lat','lon'])
    
    all_gs=gpd.GeoSeries([ShpPt(r['lon'],r['lat']) for _,r in pdf.iterrows()],crs="EPSG:4326").to_crs("EPSG:3857")
    port_zone=prepared.prep(all_gs.buffer(25000).to_crs("EPSG:4326").union_all())
    
    sanctioned=['russia','iran','venezuela','iraq','sudan','syria','north korea','libya']
    san_pdf=pdf[pdf['oil_country'].apply(lambda x:any(s in str(x).lower() for s in sanctioned))]
    san_gs=gpd.GeoSeries([ShpPt(r['lon'],r['lat']) for _,r in san_pdf.iterrows()],crs="EPSG:4326").to_crs("EPSG:3857")
    san_zone=prepared.prep(san_gs.buffer(25000).to_crs("EPSG:4326").union_all())
    print(f"港口: {len(pdf)}全部/{len(san_pdf)}制裁")

    pf=pq.ParquetFile(str(PARQUET)); all_mmsi=set()
    for rg in range(pf.metadata.num_row_groups):
        for c in range(pf.metadata.row_group(rg).num_columns):
            if pf.metadata.row_group(rg).column(c).path_in_schema=="mmsi":
                s=pf.metadata.row_group(rg).column(c).statistics
                if s and s.min is not None: all_mmsi.add(int(s.min)); all_mmsi.add(int(s.max))
    mlist=sorted(all_mmsi); print(f"MMSI: {len(mlist)}")

    results=[]; t2=time.time()
    for idx,mmsi in enumerate(mlist):
        tbl=pq.read_table(str(PARQUET),filters=[("mmsi","=",mmsi)]); df=tbl.to_pandas(); n=len(df)
        if n<2:
            results.append({"mmsi":mmsi,"msr":0,"spc":0,"sdr":0,"port_dwell":0,"port_interval":0,"turn_nonport":0,"san_port_dwell":0,"san_of_port":0}); continue
        sp=df["speed_knots"].values.astype(float); lt=df["latitude"].values.astype(float)
        ln=df["longitude"].values.astype(float); ts=df["acqtime"].values; cg=df["cog_deg"].values.astype(float)

        # MSR
        m=wilson(int(np.sum((sp>=1)&(sp<8))),n); msr=m[2]
        # SPC
        dlat=np.diff(lt);dlon=np.diff(ln);dt_h=np.diff(ts.astype("int64"))/1e9/3600;dt_h[dt_h<0.001]=0.001
        ikt=np.sqrt(dlat**2+dlon**2)*111.0/dt_h/1.852; ra=(sp[:-1]+sp[1:])/2
        v=(ikt<50)&(ra<30); spc=fisher(np.corrcoef(ra[v],ikt[v])[0,1] if v.sum()>10 else 0, int(v.sum()))[2]
        # SDR
        df["day"]=pd.to_datetime(ts).floor("D"); sd=0; td=0
        for d,g in df.groupby("day"):
            td+=1
            if g["latitude"].max()-g["latitude"].min()<0.01 and g["longitude"].max()-g["longitude"].min()<0.01: sd+=1
        sdr=wilson(sd,td)[2]

        # 港口判断
        in_port=np.zeros(n,dtype=bool); in_san=np.zeros(n,dtype=bool); batch=5000
        for i in range(0,n,batch):
            end=min(i+batch,n); pts=[ShpPt(ln[j],lt[j]) for j in range(i,end)]
            in_port[i:end]=[port_zone.contains(p) for p in pts]
            in_san[i:end]=[san_zone.contains(p) for p in pts]
        
        pd_lo,pd_hi,port_d=wilson(int(in_port.sum()),n)
        san_lo,san_hi,san_pd=wilson(int(in_san.sum()),n)
        san_of_port=round(int(in_san.sum())/int(in_port.sum()),6) if in_port.sum()>0 else 0.0

        # port_interval
        dlat=np.diff(lt);dlon=np.diff(ln);dkm=np.sum(np.sqrt(dlat**2+dlon**2)*111.0)
        calls=0; s1=False; s0=0
        for i in range(n):
            if in_port[i] and sp[i]<3:
                if not s1: s1=True; s0=i
            elif s1:
                dur=(ts[i-1].astype("int64")-ts[s0].astype("int64"))/1e9/3600
                if dur>4: calls+=1
                s1=False
        if s1:
            dur=(ts[-1].astype("int64")-ts[s0].astype("int64"))/1e9/3600
            if dur>4: calls+=1
        pi=round(calls/(dkm/1000),4) if dkm>100 else 0.0

        # turn_nonport
        tns=0; tnp=0; dn=False; pk=0; st=0
        for i in range(1,n):
            if not dn and sp[i-1]>8 and sp[i]<=8: dn=True; st=i; pk=i
            elif dn and sp[i]<sp[pk]: pk=i
            elif dn and sp[pk]<3 and sp[i]>8:
                mx=np.max(cg[st:i+1]);mn=np.min(cg[st:i+1]);cr=mx-mn
                if cr>180: cr=360-cr
                if cr>30: tns+=1
                if not in_port[st:i+1].any(): tnp+=1
                dn=False
            elif dn and sp[i]>8 and sp[pk]>=3: dn=False
        tnr=wilson(tnp,tns)[2]

        results.append({"mmsi":mmsi,"msr":msr,"spc":spc,"sdr":sdr,"port_dwell":port_d,"port_interval":pi,"turn_nonport":tnr,"san_port_dwell":san_pd,"san_of_port":san_of_port})

        if (idx+1)%50==0 or idx==len(mlist)-1:
            pct=(idx+1)/len(mlist)*100; ela=time.time()-t2
            eta=ela/(idx+1)*(len(mlist)-idx-1) if idx>0 else 0
            print(f"  [{pct:3.0f}%] {idx+1}/{len(mlist)} | {ela:.0f}s | ETA {eta:.0f}s",flush=True)
        del df,tbl

    out=pd.DataFrame(results).sort_values("msr")
    out.to_csv(OUTPUT/"ais_indicators_v3.csv",index=False,encoding="utf-8-sig")
    print(f"\n保存: {time.time()-t0:.0f}s")
    for c in ["msr","spc","sdr","port_dwell","port_interval","turn_nonport","san_port_dwell","san_of_port"]:
        v=out[c].dropna(); print(f"  {c}: mean={v.mean():.3f} median={v.median():.3f}")

if __name__=="__main__": main()
