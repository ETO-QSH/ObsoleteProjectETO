"""
消融 v4 — 含新v3指标(msr/spc/sdr)
"""
import sys; sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent.parent/"src_final"))
import pandas as pd, numpy as np
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import recall_score, precision_score, f1_score, roc_auc_score
import warnings; warnings.filterwarnings('ignore')

ROOT=Path(__file__).parent.parent; OUTPUT=ROOT/"output_final"; np.random.seed(42)
df=pd.read_csv(OUTPUT/"vessel_risk_profile.csv")
m=pd.read_csv(OUTPUT/"sanctions_matrix.csv"); m["mmsi"]=pd.to_numeric(m["mmsi"],errors="coerce").astype("Int64")
any_s=set(m[m["sanction_sources"].fillna(0)>0]["mmsi"].dropna().astype(int))
pos=df[(df["mmsi"].isin(any_s))&(df["confidence_grade"].isin(["A","B"]))]
neg=df[(~df["mmsi"].isin(any_s))&(df["confidence_grade"].isin(["A","B"]))]
y=np.concatenate([np.ones(len(pos)),np.zeros(len(neg))])
skf=StratifiedKFold(5,shuffle=True,random_state=42)

ALL=["gap_24h_ratio","non_anch_low_ratio","cog_high_vol_ratio",
     "loitering_h_ratio","non_anch_low_max_dur_h","cog_very_high_vol_ratio",
     "non_anch_low_events","msr","spc","sdr","port_dwell","port_interval","turn_nonport",
     "san_port_dwell","san_of_port","company_count","age_risk","flag_score"]
ALL=[f for f in ALL if f in df.columns and df[f].std()>0]

def cv(feats):
    feats=[f for f in feats if f in df.columns and df[f].std()>0]
    X=pd.concat([pos[feats],neg[feats]]).fillna(0); recs=[]
    for tr,te in skf.split(X,y):
        sc=StandardScaler(); X_tr=sc.fit_transform(X.iloc[tr]); X_te=sc.transform(X.iloc[te])
        m=LogisticRegression(max_iter=2000,C=1.0,solver='saga',class_weight='balanced')
        m.fit(X_tr,y[tr]); recs.append(recall_score(y[te],m.predict(X_te)))
    return np.mean(recs),np.std(recs)

results=[]
br,bs=cv(ALL)
print(f"消融 v4 | 正={len(pos)} 负={len(neg)} | 基线({len(ALL)}特征) Recall={br:.1%}±{bs:.0%}")
results.append({"实验":"全部18特征 (基线)","特征数":len(ALL),"RF_Recall":f"{br:.1%}±{bs:.0%}","ΔRF":"基线"})
print(f"\n{'实验':<28s} {'n':>2s} {'Recall':>11s} {'ΔRecall':>8s}")
print("-"*55)
for f in ALL:
    r,s=cv([x for x in ALL if x!=f])
    print(f"- {f:<26s} {len(ALL)-1:>2d} {r:>9.1%}±{s:.0%} {r-br:>+7.1%}")
    results.append({"实验":f"- {f}","特征数":len(ALL)-1,"RF_Recall":f"{r:.1%}±{s:.0%}","ΔRF":f"{r-br:+.1%}"})
for lb,grp in [("- 全部治理(3)",[x for x in ALL if x not in ["age_risk","flag_score","company_count"]]),
               ("- flag_score",[x for x in ALL if x!="flag_score"]),
               ("- company_count(Equasis)",[x for x in ALL if x!="company_count"]),
               ("- age_risk",[x for x in ALL if x!="age_risk"]),
               ("- 靠港组(3)",[x for x in ALL if x not in ["port_dwell","port_interval","turn_nonport"]]),
               ("仅治理(3)",["age_risk","flag_score","company_count"]),
               ("仅靠港+制裁港+Equasis",["port_dwell","port_interval","turn_nonport","san_port_dwell","san_of_port","company_count"]),
               ("仅v3(msr/spc/sdr)",["msr","spc","sdr"])]:
    r,s=cv(grp); print(f"{lb:<28s} {len(grp):>2d} {r:>9.1%}±{s:.0%} {r-br:>+7.1%}")
    results.append({"实验":lb,"特征数":len(grp),"RF_Recall":f"{r:.1%}±{s:.0%}","ΔRF":f"{r-br:+.1%}"})
import pandas as pd; pd.DataFrame(results).to_csv(OUTPUT/"ablation_final.csv",index=False,encoding='utf-8-sig')
