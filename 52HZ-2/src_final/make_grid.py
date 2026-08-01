"""多指标热力图: 支持参数选择"""
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

grids={m:np.zeros((len(trees_range),len(depths))) for m in ['R','P','F1','AUC','std']}
print(f"Grid: {len(trees_range)}×{len(depths)}×5折 = {len(trees_range)*len(depths)*5} fits")
for ti,nt in enumerate(trees_range):
    for di,md in enumerate(depths):
        c_r=[]; c_p=[]; c_f=[]; c_a=[]; c_s=[]
        for tr,te in skf.split(X,y):
            rf=RandomForestClassifier(n_estimators=nt,max_depth=md,min_samples_leaf=8,class_weight='balanced',random_state=42)
            rf.fit(X.iloc[tr],y[tr]); yp=rf.predict(X.iloc[te]); yb=rf.predict_proba(X.iloc[te])[:,1]
            c_r.append(recall_score(y[te],yp)); c_p.append(precision_score(y[te],yp,zero_division=0))
            c_f.append(f1_score(y[te],yp,zero_division=0)); c_a.append(roc_auc_score(y[te],yb))
            tp=np.array([t.predict_proba(X.iloc[te])[:,1] for t in rf.estimators_]); c_s.append(tp.std(axis=0).mean())
        grids['R'][ti,di]=np.mean(c_r); grids['P'][ti,di]=np.mean(c_p)
        grids['F1'][ti,di]=np.mean(c_f); grids['AUC'][ti,di]=np.mean(c_a)
        grids['std'][ti,di]=np.mean(c_s)
        print(f"  t={nt:>3d} d={md}  R={np.mean(c_r):.3f} P={np.mean(c_p):.3f} F1={np.mean(c_f):.3f} AUC={np.mean(c_a):.3f} std={np.mean(c_s):.4f}")

# 4面板热力图
fig,axes=plt.subplots(2,2,figsize=(12,9))
for ax,(title,cmap,vmin,vmax,fmt) in zip(axes.flat, [
    ('Recall (R)', 'YlOrRd', 0.78, 0.85, '.3f'),
    ('Precision (P)', 'YlGnBu', 0.75, 0.83, '.3f'),
    ('F1 Score', 'RdYlGn', 0.77, 0.83, '.3f'),
    ('AUC', 'Purples', 0.87, 0.91, '.3f'),
]):
    g=grids[title[:3].strip('(').strip(')')] if 'Recall' in title else grids[title.split()[0]]
    im=ax.imshow(g,cmap=cmap,aspect='auto',vmin=vmin,vmax=vmax)
    ax.set_xticks(range(len(depths))); ax.set_xticklabels(depths)
    ax.set_yticks(range(len(trees_range))); ax.set_yticklabels(trees_range)
    ax.set_xlabel('max_depth',fontsize=10); ax.set_ylabel('n_estimators',fontsize=10)
    ax.set_title(title,fontsize=12,fontweight='bold')
    # 框选最优点
    best=np.unravel_index(np.argmax(g),g.shape) if 'std' not in title else np.unravel_index(np.argmin(g),g.shape)
    ax.add_patch(plt.Rectangle((best[1]-0.5,best[0]-0.5),1,1,fill=False,edgecolor='black',linewidth=2.5))
    # 标值
    for i in range(len(trees_range)):
        for j in range(len(depths)):
            color='white' if g[i,j]> (vmin+vmax)/2 else 'black'
            ax.text(j,i,f'{g[i,j]:{fmt}}',ha='center',va='center',fontsize=7,color=color,fontweight='bold')
    plt.colorbar(im,ax=ax,shrink=0.85)

plt.suptitle('RF参数网格 (5折CV)',fontsize=15,fontweight='bold',y=1.01)
plt.tight_layout(); plt.savefig(CHARTS/'param_grid.png',dpi=150); plt.close()
print(f"\nSaved: param_grid.png")
print(f"F1最优: t={trees_range[np.unravel_index(np.argmax(grids['F1']),grids['F1'].shape)[0]]} d={depths[np.unravel_index(np.argmax(grids['F1']),grids['F1'].shape)[1]]} F1={grids['F1'].max():.3f}")
