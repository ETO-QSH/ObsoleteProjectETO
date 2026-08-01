"""ROC + Youden 阈值图"""
import sys; sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent.parent/"src_final"))
import pandas as pd, numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_curve, roc_auc_score
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
FEATS=["msr","spc","sdr","port_dwell","port_interval","turn_nonport","san_port_dwell","san_of_port","company_count","age_risk","flag_score",
       "gap_24h_ratio","non_anch_low_ratio","cog_high_vol_ratio","loitering_h_ratio","non_anch_low_max_dur_h","cog_very_high_vol_ratio","non_anch_low_events"]
FEATS=[f for f in FEATS if f in df.columns and df[f].std()>0]
X=pd.concat([pos[FEATS],neg[FEATS]]).fillna(0); y=np.concatenate([np.ones(len(pos)),np.zeros(len(neg))])

rf=RandomForestClassifier(n_estimators=100,max_depth=2,min_samples_leaf=8,class_weight='balanced',random_state=42)
rf.fit(X,y); yb=rf.predict_proba(X)[:,1]
fpr,tpr,thresholds=roc_curve(y,yb)
auc=roc_auc_score(y,yb)
youden=tpr-fpr; best=np.argmax(youden)
best_th=thresholds[best]*100

fig,ax=plt.subplots(figsize=(6,5.5))
ax.plot(fpr,tpr,'-',color='#4472C4',linewidth=2.5,label=f'ROC (AUC={auc:.3f})')
ax.plot([0,1],[0,1],'--',color='gray',alpha=0.5,linewidth=1)
ax.scatter(fpr[best],tpr[best],color='#C00000',s=120,zorder=5,
          edgecolors='white',linewidth=1.5)
ax.annotate(f'Youden最优\n阈值={best_th:.1f}\n灵敏度={tpr[best]:.1%}\n特异度={1-fpr[best]:.1%}',
           xy=(fpr[best],tpr[best]),xytext=(fpr[best]+0.25,tpr[best]-0.12),
           fontsize=10,fontweight='bold',color='#C00000',
           arrowprops=dict(arrowstyle='->',color='#C00000',lw=1.5),
           bbox=dict(boxstyle='round,pad=0.3',facecolor='white',alpha=0.9,edgecolor='#C00000'))
ax.set_xlabel('1 - 特异度 (假阳性率)',fontsize=11)
ax.set_ylabel('灵敏度 (召回率)',fontsize=11)
ax.set_title('ROC曲线与Youden最优阈值',fontsize=13,fontweight='bold',pad=12)
ax.legend(loc='lower right',fontsize=9)
ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig(CHARTS/'roc_youden.png',dpi=150); plt.close()
print(f"AUC={auc:.3f}  Youden={youden[best]:.3f}  阈值={best_th:.1f}")
print("Saved: roc_youden.png")
