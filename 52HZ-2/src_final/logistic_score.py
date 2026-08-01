"""
影子船队经验公式 v4
=====================
正样本: 任何制裁命中, A/B级 (AFRAMAX=全运油)
"""
import sys; sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent.parent/"src_final"))
import pandas as pd, numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, roc_curve
import warnings; warnings.filterwarnings('ignore')

ROOT=Path(__file__).parent.parent; OUTPUT=ROOT/"output_final"; np.random.seed(42)

df=pd.read_csv(OUTPUT/"vessel_risk_profile.csv")
matrix=pd.read_csv(OUTPUT/"sanctions_matrix.csv")
matrix["mmsi"]=pd.to_numeric(matrix["mmsi"],errors="coerce").astype("Int64")

FEATURES=["gap_24h_ratio","non_anch_low_ratio","cog_high_vol_ratio",
          "loitering_h_ratio","non_anch_low_max_dur_h","cog_very_high_vol_ratio",
          "non_anch_low_events","age_risk","flag_score",
          "msr","spc","sdr","port_dwell","port_interval","turn_nonport","san_port_dwell","san_of_port","company_count",
          "total_identity_changes","name_changes","flag_changes","owner_changes",
          "unrecorded_call_ratio","recorded_calls","hotspot_dwell_ratio"]
FEATURES=[f for f in FEATURES if f in df.columns and df[f].std()>0]
print(f"特征: {len(FEATURES)} — {FEATURES}")

any_mmsi=set(matrix[matrix["sanction_sources"].fillna(0)>0]["mmsi"].dropna().astype(int))
pos=df[(df["mmsi"].isin(any_mmsi))&(df["confidence_grade"].isin(["A","B"]))]
neg=df[(~df["mmsi"].isin(any_mmsi))&(df["confidence_grade"].isin(["A","B"]))]
X=pd.concat([pos[FEATURES],neg[FEATURES]]).fillna(0)
y=np.concatenate([np.ones(len(pos)),np.zeros(len(neg))])
print(f"正={int(y.sum())} 负={len(y)-int(y.sum())} 比={len(y)/y.sum():.1f}:1")

rf=RandomForestClassifier(n_estimators=100,max_depth=2,min_samples_leaf=8,class_weight='balanced',random_state=42)
rf.fit(X,y); rf_p=rf.predict_proba(X)[:,1]
print(f"\nRF train {rf.score(X,y):.3f}")
print(classification_report(y,rf.predict(X),target_names=['负','正'],digits=3))

sc=StandardScaler(); Xs=sc.fit_transform(X)
lr=LogisticRegression(max_iter=2000,C=1.0,solver='saga',class_weight='balanced')
lr.fit(Xs,y); lr_p=lr.predict_proba(Xs)[:,1]
print(f"LR train {lr.score(Xs,y):.3f}")
print(classification_report(y,lr.predict(Xs),target_names=['负','正'],digits=3))

ep=(rf_p+lr_p)/2
print(f"Ens train {((ep>=0.5).astype(int)==y).mean():.3f}")
print(classification_report(y,(ep>=0.5).astype(int),target_names=['负','正'],digits=3))

def youden(yt,yp): fpr,tpr,_=roc_curve(yt,yp); return max(tpr-fpr)
models={"RF":(rf,None,rf_p),"LR":(lr,sc,lr_p),"Ensemble":(None,None,ep)}
best=max(models,key=lambda k:youden(y,models[k][2]))
print(f"\n最优: {best} (Youden={youden(y,models[best][2]):.3f})")

# 全量预测
X_all=df[FEATURES].fillna(0)
if best=="RF":
    df["logistic_score"]=(rf.predict_proba(X_all)[:,1]*100).round(2)
    t=np.array([t.predict_proba(X_all)[:,1] for t in rf.estimators_])
    df["logistic_score_std"]=(t.std(axis=0)*100).round(2); w=pd.Series(rf.feature_importances_,index=FEATURES)
elif best=="LR":
    df["logistic_score"]=(lr.predict_proba(sc.transform(X_all))[:,1]*100).round(2)
    df["logistic_score_std"]=8.0; w=pd.Series(np.abs(lr.coef_[0]),index=FEATURES)
else:
    df["logistic_score"]=((rf.predict_proba(X_all)[:,1]+lr.predict_proba(sc.transform(X_all))[:,1])/2*100).round(2)
    df["logistic_score_std"]=(np.std([rf.predict_proba(X_all)[:,1],lr.predict_proba(sc.transform(X_all))[:,1]],axis=0)*100).round(2)
    w=pd.Series(rf.feature_importances_,index=FEATURES)

w=(w/w.sum()).round(4)
df["logistic_score_ci95_lower"]=(df["logistic_score"]-1.96*df["logistic_score_std"]).clip(0,100).round(2)
df["logistic_score_ci95_upper"]=(df["logistic_score"]+1.96*df["logistic_score_std"]).clip(0,100).round(2)

yp=models[best][2]; fpr,tpr,ths=roc_curve(y,yp); idx=np.argmax(tpr-fpr); th=ths[idx]*100
print(f"\n最优阈值={th:.1f} 灵敏度={tpr[idx]:.1%} 特异度={1-fpr[idx]:.1%}")

# 四象限
def q(row):
    h=row["logistic_score"]>=th; s=row["mmsi"] in any_mmsi
    if h and s: return "A_确认影子"
    if h: return "B_潜在影子"
    if s: return "C_名单被动"
    return "D_正常"
df["quadrant"]=df.apply(q,axis=1)

san_set=df[df["mmsi"].isin(any_mmsi)]
A=(san_set["quadrant"]=="A_确认影子").sum(); C=(san_set["quadrant"]=="C_名单被动").sum()
rec=A/(A+C) if A+C>0 else 0

print(f"\n四象限 ({best}, Youden阈值={th:.1f}) | 纵轴=任何制裁({len(any_mmsi)}艘)")
for qq in ["A_确认影子","B_潜在影子","C_名单被动","D_正常"]:
    sub=df[df["quadrant"]==qq]
    if len(sub)==0: continue
    print(f"  {qq:12s} {len(sub):>5d} {len(sub)/len(df)*100:>5.1f}% 制裁={sub['mmsi'].isin(any_mmsi).sum():>3d} 均分={sub['logistic_score'].mean():.1f}")
print(f"  Recall={rec:.1%}")

def cred(r):
    ok_std=r.get("logistic_score_std",999)<25; ok_data=r.get("confidence_grade","C") in ["A","B"]
    return "高可信" if ok_std and ok_data else ("中可信" if ok_std or ok_data else "低可信")
df["prediction_credibility"]=df.apply(cred,axis=1)

print(f"\n权重: {w.sort_values(ascending=False).to_string()}")
print(f"可信度: 高={(df['prediction_credibility']=='高可信').sum()} 中={(df['prediction_credibility']=='中可信').sum()} 低={(df['prediction_credibility']=='低可信').sum()}")

bs=df[df["quadrant"]=="B_潜在影子"].nlargest(10,"logistic_score")
print(f"\nB象限 Top 10:")
for _,r in bs.iterrows():
    print(f"  {str(r.get('ship_name','?')):25s} {r['logistic_score']:.1f} | {r.get('country','')}")

w.to_frame("weight").assign(pct=(w*100).round(1).astype(str)+"%").to_csv(OUTPUT/"logistic_weights.csv",encoding="utf-8-sig")
orig=pd.read_csv(OUTPUT/"vessel_risk_profile.csv")
for c in ["logistic_score","logistic_score_std","logistic_score_ci95_lower","logistic_score_ci95_upper","prediction_credibility","quadrant"]:
    if c in df.columns: orig[c]=df[c]
orig.to_csv(OUTPUT/"vessel_risk_profile.csv",index=False,encoding="utf-8-sig")
idc=[c for c in ["mmsi","ship_name","country"] if c in df.columns]
extra=[c for c in ["logistic_score","logistic_score_std","logistic_score_ci95_lower","logistic_score_ci95_upper","prediction_credibility","anomaly_index","confidence_grade","sanction_sources","hit_ofac","quadrant"] if c in df.columns]
df[idc+FEATURES+extra].sort_values("logistic_score",ascending=False).to_csv(OUTPUT/"vessel_risk_simple.csv",index=False,encoding="utf-8-sig")
print(f"\n完成 — {best} — Recall={rec:.1%}")
