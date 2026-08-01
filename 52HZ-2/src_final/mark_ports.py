import pandas as pd
from pathlib import Path

ROOT=Path(r'D:\Desktop\Desktop\海事')
df=pd.read_csv(ROOT/'决赛资料'/'原油装卸港清单'/'原油装卸港清单_详细.csv')

sanctioned=['Russia','Iran','Venezuela','Iraq','Sudan','Syria','North Korea','Libya']
df['is_sanctioned']=df['oil_country'].apply(
    lambda x: any(s.lower() in str(x).lower() for s in sanctioned))

san=df[df['is_sanctioned']]
print(f'制裁国港口: {len(san)} / {len(df)}')
for _,r in san.iterrows():
    print(f"  {r['oil_country']:20s} {r['oil_port']}")

out=ROOT/'决赛资料'/'原油装卸港清单'/'港口制裁标记.csv'
df[['oil_country','oil_port','port_type','lat','lon','is_sanctioned']].to_csv(out,index=False,encoding='utf-8-sig')
print(f'\nSaved: {out}')
