"""PPT图表 v3 — 18特征版"""
import pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path; import warnings; warnings.filterwarnings('ignore')

ROOT=Path(__file__).parent.parent; OUTPUT=ROOT/"output_final"; CHARTS=OUTPUT/"charts"
CHARTS.mkdir(parents=True,exist_ok=True)
plt.rcParams['font.family']='Microsoft YaHei'; plt.rcParams['axes.unicode_minus']=False

df=pd.read_csv(OUTPUT/"vessel_risk_profile.csv")

# ===== 1. 饼图 =====
major=[('船旗评分 (flag_score)',27.6,'#1F4E79'),('Equasis变更 (company_count)',27.0,'#2E75B6'),
       ('靠港频率 (port_interval)',15.8,'#5B9BD5'),('船龄分级 (age_risk)',8.1,'#ED7D31'),
       ('港口时间占比 (port_dwell)',7.1,'#70AD47')]
other_sum=100-sum(x[1] for x in major)
pie_data=major+[(f'其他指标 (13项)',other_sum,'#D0D0D0')]
labels=[x[0] for x in pie_data]; vals=[x[1] for x in pie_data]; colors=[x[2] for x in pie_data]
fig,(ax_pie,ax_leg)=plt.subplots(1,2,figsize=(12,5.5),gridspec_kw={'width_ratios':[1.2,1]})
ax_pie.pie(vals,labels=None,colors=colors,autopct=lambda pct:f'{pct:.1f}%' if pct>3 else '',
           startangle=140,pctdistance=0.6,wedgeprops={'edgecolor':'white','linewidth':1.5})
ax_leg.axis('off')
handles=[plt.Rectangle((0,0),1,1,facecolor=c,edgecolor='white',linewidth=1) for c in colors]
ax_leg.legend(handles,[f'{l}  {v:.1f}%' for l,v in zip(labels,vals)],loc='center',fontsize=10,frameon=False)
ax_pie.set_title('Random Forest 特征重要性分布',fontsize=14,fontweight='bold',pad=15)
plt.tight_layout(); plt.savefig(CHARTS/'rf_weights.png',dpi=150); plt.close()
print('1/4 rf_weights.png')

# ===== 2. 四象限 =====
fig,ax=plt.subplots(figsize=(8,5.5))
df['is_san']=(df['sanction_sources'].fillna(0)>0)
actual_th=df[df['quadrant'].isin(['A_确认影子','B_潜在影子'])]['logistic_score'].min()
df['xc']=df['logistic_score']-actual_th
rng=np.random.default_rng(42)
san=df[df['is_san']]; unsan=df[~df['is_san']]
san_y=np.clip((san['sanction_sources'].fillna(1)/4).values+rng.uniform(-0.08,0.08,len(san)),0.05,1.0)
unsan_y=-(rng.uniform(0.05,1.0,len(unsan)))
ax.scatter(san['xc'],san_y,c='#C00000',alpha=0.45,s=16,edgecolors='none')
ax.scatter(unsan['xc'],unsan_y,c='#4472C4',alpha=0.35,s=14,edgecolors='none')
ax.axvline(x=0,color='black',linestyle='--',alpha=0.5,linewidth=1.2)
ax.axhline(y=0,color='black',linestyle='--',alpha=0.5,linewidth=1.2)
ax.set_xlabel(f'logistic_score − {actual_th:.1f}',fontsize=11)
ax.set_ylabel('制裁命中',fontsize=11)
ax.set_title(f'四象限分布（Youden阈值={actual_th:.1f}）',fontsize=13,fontweight='bold')
A_n=(df['quadrant']=='A_确认影子').sum(); B_n=(df['quadrant']=='B_潜在影子').sum()
C_n=(df['quadrant']=='C_名单被动').sum(); D_n=(df['quadrant']=='D_正常').sum()
for label,x,y,color in [(f'A 确认影子\n{A_n}艘',22.5,0.5,'#C00000'),
    (f'B 潜在发现\n{B_n}艘',22.5,-0.5,'#ED7D31'),
    (f'C 名单被动\n{C_n}艘',-22.5,0.5,'#4472C4'),
    (f'D 正常\n{D_n}艘',-22.5,-0.5,'#70AD47')]:
    ax.annotate(label,xy=(x,y),fontsize=10,fontweight='bold',color=color,ha='center',
                bbox=dict(boxstyle='round,pad=0.3',facecolor='white',alpha=0.85,edgecolor=color,linewidth=1.2))
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
ax.set_yticks([-1,0,1])
plt.tight_layout(); plt.savefig(CHARTS/'quadrant.png',dpi=150); plt.close()
print('2/4 quadrant.png')

# ===== 3. 消融 =====
ab=pd.read_csv(OUTPUT/"ablation_final.csv")
ab['v']=ab['RF_Recall'].str.extract(r'([\d.]+)').astype(float)
# 0=基线, 1=-flag, 16=-company_count, 17=-age, 15=-治理, 18=-靠港, 19=仅治理, 20=仅靠港+Equasis, 21=仅v3
rows=[0,1,16,17,15,18,19,20,21]
labs=['18特征\n(基线)','-flag_score','-company_count','-age_risk',
      '-治理(2)','-靠港(3)','仅治理(2)','仅靠港+\nEquasis(6)','仅v3(3)']
cols=['#4472C4']+['#C00000']*4+['#70AD47']*3
vals=[ab.iloc[r]['v'] for r in rows]
fig,ax=plt.subplots(figsize=(9,4.5))
bars=ax.bar(range(len(vals)),vals,color=cols,edgecolor='white',width=0.7)
bl=vals[0]
for b,v in zip(bars,vals):
    d=v-bl; c='red' if d<-1 else ('green' if d>1 else 'gray')
    ax.text(b.get_x()+b.get_width()/2,b.get_height()+0.5,f'{v:.1f}%\n({d:+.1f}%)',
            ha='center',va='bottom',fontsize=8,color=c)
ax.set_xticks(range(len(labs))); ax.set_xticklabels(labs,fontsize=8)
ax.set_ylabel('5折CV Recall (%)',fontsize=11)
ax.set_title('消融实验 (LR, 215正样本, 18特征)',fontsize=13,fontweight='bold')
ax.axhline(y=bl,color='#4472C4',linestyle='--',alpha=0.6,linewidth=1.5)
ax.set_ylim(60,92); ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
plt.tight_layout(); plt.savefig(CHARTS/'ablation.png',dpi=150); plt.close()
print('3/4 ablation.png')

# ===== 4. 置信度 =====
cred=df['prediction_credibility'].value_counts()
fig,ax=plt.subplots(figsize=(5,4.5))
cc={'高可信':'#70AD47','中可信':'#ED7D31','低可信':'#C00000'}
ax.pie([cred.get('高可信',0),cred.get('中可信',0),cred.get('低可信',0)],
       labels=['高可信','中可信','低可信'],autopct='%1.1f%%',
       colors=[cc['高可信'],cc['中可信'],cc['低可信']],
       startangle=90,pctdistance=0.6,labeldistance=1.1,
       textprops={'fontsize':11},wedgeprops={'edgecolor':'white','linewidth':2})
ax.set_title(f'预测可信度分布 (共{len(df)}艘)',fontsize=13,fontweight='bold')
plt.tight_layout(); plt.savefig(CHARTS/'confidence.png',dpi=150); plt.close()
print('4/4 confidence.png')
print('Done')
