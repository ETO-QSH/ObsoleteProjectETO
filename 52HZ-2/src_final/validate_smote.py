"""
SMOTE 合理性验证
=================
对比: SMOTE vs 原生不平衡 vs 交叉验证
"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent.parent / "src_final"))

import pandas as pd, numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_score
from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier

ROOT = Path(__file__).parent.parent
OUTPUT = ROOT / "output_final"
np.random.seed(42)

df = pd.read_csv(OUTPUT / "vessel_risk_profile.csv")
matrix = pd.read_csv(OUTPUT / "sanctions_matrix.csv")
matrix["mmsi"] = pd.to_numeric(matrix["mmsi"], errors="coerce").astype("Int64")

FEATURES = ["gap_24h_ratio","non_anch_low_ratio","cog_high_vol_ratio",
            "loitering_h_ratio","non_anch_low_max_dur_h",
            "cog_very_high_vol_ratio","gap_max_hours","non_anch_low_events",
            "age_risk","flag_score"]
FEATURES = [f for f in FEATURES if f in df.columns and df[f].std() > 0]

oil_programs = ["RUSSIA","IRAN","VENEZUELA"]
oil_mmsi = set()
for _,r in matrix.iterrows():
    if any(p in str(r.get("sanction_detail","")).upper() for p in oil_programs):
        oil_mmsi.add(r["mmsi"])
any_mmsi = set(matrix[matrix["sanction_sources"].fillna(0)>0]["mmsi"].dropna().astype(int))

pos = df[(df["mmsi"].isin(oil_mmsi))&(df["confidence_grade"].isin(["A","B"]))]
neg = df[(~df["mmsi"].isin(any_mmsi))&(df["confidence_grade"].isin(["A","B"]))]

X = pd.concat([pos[FEATURES], neg[FEATURES]]).fillna(0)
y = np.concatenate([np.ones(len(pos)), np.zeros(len(neg))])

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

print(f"正样本:{len(pos)} 负样本:{len(neg)} 不平衡比:{len(neg)/len(pos):.1f}:1")
print(f"\n{'='*70}")
print(f"{'方法':<20s} {'CV Recall':>10s} {'CV Prec':>10s} {'CV F1':>10s} {'CV AUC':>10s} {'Train Recall':>12s}")
print(f"{'='*70}")

for name, model, use_smote in [
    ("XGB+scale_weight", XGBClassifier(n_estimators=100,max_depth=3,reg_lambda=2,reg_alpha=1,
                     scale_pos_weight=len(neg)/len(pos),random_state=42,verbosity=0), False),
    ("XGB+SMOTE", XGBClassifier(n_estimators=100,max_depth=3,reg_lambda=2,reg_alpha=1,
                     random_state=42,verbosity=0), True),
    ("RF+balanced", RandomForestClassifier(n_estimators=300,max_depth=6,min_samples_leaf=5,
                     class_weight='balanced',random_state=42), False),
    ("RF+SMOTE", RandomForestClassifier(n_estimators=300,max_depth=6,min_samples_leaf=5,
                     random_state=42), True),
    ("LR+balanced", LogisticRegression(max_iter=2000,C=1.0,class_weight='balanced'), False),
    ("LR+SMOTE", LogisticRegression(max_iter=2000,C=1.0), True),
]:
    recalls, precs, f1s, aucs = [], [], [], []
    train_recall = 0

    for train_i, test_i in skf.split(X, y):
        X_tr, X_te = X.iloc[train_i], X.iloc[test_i]
        y_tr, y_te = y[train_i], y[test_i]

        if use_smote:
            X_tr, y_tr = SMOTE(random_state=42).fit_resample(X_tr, y_tr)

        if "LR" in name:
            sc = StandardScaler()
            X_tr = sc.fit_transform(X_tr)
            X_te = sc.transform(X_te)

        model.fit(X_tr, y_tr)
        yp = model.predict(X_te)
        yprob = model.predict_proba(X_te)[:,1] if hasattr(model,'predict_proba') else yp

        from sklearn.metrics import recall_score, precision_score, f1_score
        recalls.append(recall_score(y_te, yp))
        precs.append(precision_score(y_te, yp, zero_division=0))
        f1s.append(f1_score(y_te, yp, zero_division=0))
        aucs.append(roc_auc_score(y_te, yprob))

        if not use_smote:
            train_recall = recall_score(y_tr, model.predict(X_tr))

    best = max(range(5), key=lambda i: f1s[i])
    print(f"{name:<20s} {np.mean(recalls):>9.1%}±{np.std(recalls):.0%} {np.mean(precs):>9.1%}±{np.std(precs):.0%} {np.mean(f1s):>9.1%}±{np.std(f1s):.0%} {np.mean(aucs):>9.3f} {train_recall:>11.1%}")

print(f"\n结论: 5折CV评估，避免训练集过拟合假象。")
print(f"      Recall = 制裁船在未见数据上的召回率。")
print(f"      数值越高 → 泛化能力越强。")
