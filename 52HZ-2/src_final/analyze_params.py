"""全网格: trees × depth, 5折CV五指标"""
import sys; sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent.parent/"src_final"))
import pandas as pd, numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import recall_score, roc_auc_score, precision_score, f1_score
import warnings; warnings.filterwarnings('ignore')

ROOT=Path(__file__).parent.parent; OUTPUT=ROOT/"output_final"
df=pd.read_csv(OUTPUT/"vessel_risk_profile.csv")
m=pd.read_csv(OUTPUT/"sanctions_matrix.csv"); m["mmsi"]=pd.to_numeric(m["mmsi"],errors="coerce").astype("Int64")
any_s=set(m[m["sanction_sources"].fillna(0)>0]["mmsi"].dropna().astype(int))
pos=df[(df["mmsi"].isin(any_s))&(df["confidence_grade"].isin(["A","B"]))]
neg=df[(~df["mmsi"].isin(any_s))&(df["confidence_grade"].isin(["A","B"]))]
FEATS=["msr","spc","sdr","port_dwell","port_interval","turn_nonport","age_risk","flag_score",
       "gap_24h_ratio","non_anch_low_ratio","cog_high_vol_ratio","loitering_h_ratio","non_anch_low_max_dur_h","cog_very_high_vol_ratio","non_anch_low_events"]
FEATS=[f for f in FEATS if f in df.columns and df[f].std()>0]
X=pd.concat([pos[FEATS],neg[FEATS]]).fillna(0); y=np.concatenate([np.ones(len(pos)),np.zeros(len(neg))])
skf=StratifiedKFold(5,shuffle=True,random_state=42)

trees_range=[50,60,70,80,90,100,110,120]
depth_range=[2,3,4,5,6,7,8,9]
total=len(trees_range)*len(depth_range)*5
print(f"trees={trees_range}\ndepth={depth_range}\n组合={len(trees_range)*len(depth_range)} × 5折 = {total} fits\n")

results=[]
for nt in trees_range:
    for md in depth_range:
        c_r=[]; c_p=[]; c_f=[]; c_a=[]; c_s=[]
        for tr,te in skf.split(X,y):
            rf=RandomForestClassifier(n_estimators=nt,max_depth=md,min_samples_leaf=8,class_weight='balanced',random_state=42)
            rf.fit(X.iloc[tr],y[tr]); yp=rf.predict(X.iloc[te]); yb=rf.predict_proba(X.iloc[te])[:,1]
            c_r.append(recall_score(y[te],yp)); c_p.append(precision_score(y[te],yp,zero_division=0))
            c_f.append(f1_score(y[te],yp,zero_division=0)); c_a.append(roc_auc_score(y[te],yb))
            tp=np.array([t.predict_proba(X.iloc[te])[:,1] for t in rf.estimators_]); c_s.append(tp.std(axis=0).mean())
        mr,mp,mf,ma,ms=np.mean(c_r),np.mean(c_p),np.mean(c_f),np.mean(c_a),np.mean(c_s)
        results.append((nt,md,mr,mp,mf,ma,ms))
        print(f"  t={nt:>4d} d={md}  R={mr:.3f} P={mp:.3f} F1={mf:.3f} AUC={ma:.3f} std={ms:.4f}")

# 找最优(按F1)
best=sorted(results,key=lambda x: x[4],reverse=True)[0]
print(f"\n最优: trees={best[0]} depth={best[1]} F1={best[4]:.3f} R={best[2]:.3f} AUC={best[5]:.3f} std={best[6]:.4f}")
