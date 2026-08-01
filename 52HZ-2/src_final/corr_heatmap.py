"""指标相关性热力图: R/P/F1/AUC/std"""
import sys; sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent.parent/"src_final"))
import pandas as pd, numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import recall_score, roc_auc_score, precision_score, f1_score
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings; warnings.filterwarnings('ignore')

ROOT=Path(__file__).parent.parent; OUTPUT=ROOT/"output_final"; CHARTS=OUTPUT/"charts"
CHARTS.mkdir(parents=True,exist_ok=True)
plt.rcParams['font.family']='Microsoft YaHei'; plt.rcParams['axes.unicode_minus']=False

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
depths=[2,3,4,5,6,7,8,9]

rows=[]
print(f"Grid: {len(trees_range)}×{len(depths)}={len(trees_range)*len(depths)} combos")
for nt in trees_range:
    for md in depths:
        c_r=[]; c_p=[]; c_f=[]; c_a=[]; c_s=[]
        for tr,te in skf.split(X,y):
            rf=RandomForestClassifier(n_estimators=nt,max_depth=md,min_samples_leaf=8,class_weight='balanced',random_state=42)
            rf.fit(X.iloc[tr],y[tr]); yp=rf.predict(X.iloc[te]); yb=rf.predict_proba(X.iloc[te])[:,1]
            c_r.append(recall_score(y[te],yp)); c_p.append(precision_score(y[te],yp,zero_division=0))
            c_f.append(f1_score(y[te],yp,zero_division=0)); c_a.append(roc_auc_score(y[te],yb))
            tp=np.array([t.predict_proba(X.iloc[te])[:,1] for t in rf.estimators_]); c_s.append(tp.std(axis=0).mean())
        rows.append([nt,md,np.mean(c_r),np.mean(c_p),np.mean(c_f),np.mean(c_a),np.mean(c_s)])
        print(f"  t={nt:>3d} d={md}  R={np.mean(c_r):.3f} P={np.mean(c_p):.3f} F1={np.mean(c_f):.3f} AUC={np.mean(c_a):.3f} std={np.mean(c_s):.4f}")

data=pd.DataFrame(rows,columns=['trees','depth','R','P','F1','AUC','std'])
metric_cols=['R','P','F1','AUC','std']
corr=data[metric_cols].corr()

fig,ax=plt.subplots(figsize=(6,5))
im=ax.imshow(corr,cmap='RdBu_r',vmin=-1,vmax=1,aspect='auto')
ax.set_xticks(range(len(metric_cols))); ax.set_xticklabels(['Recall','Precision','F1','AUC','σ'],fontsize=12)
ax.set_yticks(range(len(metric_cols))); ax.set_yticklabels(['Recall','Precision','F1','AUC','σ'],fontsize=12)
for i in range(len(metric_cols)):
    for j in range(len(metric_cols)):
        color='white' if abs(corr.iloc[i,j])>0.6 else 'black'
        ax.text(j,i,f'{corr.iloc[i,j]:.3f}',ha='center',va='center',fontsize=14,fontweight='bold',color=color)
ax.set_title('指标相关性热力图 (64组参数 × 5折CV)',fontsize=13,fontweight='bold',pad=12)
plt.colorbar(im,ax=ax,shrink=0.82)
plt.tight_layout(); plt.savefig(CHARTS/'corr_heatmap.png',dpi=150); plt.close()
print(f"\nSaved: corr_heatmap.png")
print(corr.to_string())
