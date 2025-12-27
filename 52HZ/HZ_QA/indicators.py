import pandas as pd

from database.datalib import get_ships


# ---------- 1. 船舶密度 ----------
def density_2h(gdf) -> pd.DataFrame:
    return gdf.groupby('interval')['mmsi'].nunique().reset_index(name='rho')


# ---------- 2. 航迹冲突 ----------
def conflict_2h(gdf) -> pd.DataFrame:
    MAX_PAIR = 1000
    conflicts = []

    for h, grp in gdf.groupby('interval'):
        n = len(grp)
        if n < 2:
            continue
        if n > MAX_PAIR:
            grp = grp.sample(MAX_PAIR, random_state=42)
        cog = grp['cog'].to_numpy()
        step = max(1, len(cog) // MAX_PAIR)
        for i in range(0, len(cog), step):
            for j in range(i + 1, len(cog), step):
                if abs(cog[i] - cog[j]) > 45:
                    conflicts.append({'interval': h})
    return pd.DataFrame(conflicts).groupby('interval').size().reset_index(name='C')


# ---------- 3. 平均航速 ----------
def speed_2h(gdf) -> pd.DataFrame:
    return gdf.groupby('interval')['speed'].mean().reset_index(name='speed')


# ---------- 4. 运力分布 ----------
def teu_2h(gdf) -> pd.DataFrame:
    ships = get_ships().set_index('ship_mmsi')
    teu_extract = (
        ships['ship_size']
        .astype(str)
        .str.extract(r'([\d,]+)\s*(?:TEU|CEU)', expand=False)
        .str.replace(',', '', regex=False)
        .astype(float)
        .fillna(0)
        .astype(int)
    )
    ships = ships.assign(teu=teu_extract)
    gdf = gdf.merge(ships[['teu']], left_on='mmsi', right_index=True)
    return gdf.groupby('interval')['teu'].sum().reset_index(name='ΔM')
