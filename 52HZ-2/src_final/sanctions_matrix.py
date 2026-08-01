"""
四合一制裁名单筛查（OFAC + UN + EU + UK）
=============================================
输出每艘船在四个制裁名单中的命中矩阵
"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent.parent / "src_final"))

import pandas as pd
import re
import time
from pathlib import Path
from io import StringIO
from datalib_final import get_ship_archive, get_all_mmsi

ROOT = Path(__file__).parent.parent
OUTPUT = ROOT / "output_final"
EXTERNAL = ROOT / "external_final"
OUTPUT.mkdir(parents=True, exist_ok=True)

# ============================================================
# 工具函数
# ============================================================

def extract_imos(text: str) -> set[int]:
    """从文本提取所有 IMO 号"""
    imos = set()
    for m in re.findall(r'IMO[:\s]*(\d{7})', text, re.IGNORECASE):
        imos.add(int(m))
    # 宽匹配：7位数字（在合适上下文）
    for m in re.findall(r'\b(\d{7})\b', text):
        imos.add(int(m))
    return imos


# ============================================================
# 1. OFAC（已有结果）
# ============================================================

def load_ofac():
    """加载已保存的 OFAC 筛查结果"""
    path = OUTPUT / "ofac_sdn_matches.csv"
    if not path.exists():
        print("[OFAC] 无已有结果")
        return {}
    df = pd.read_csv(path)
    result = {}
    for _, row in df.iterrows():
        imo = row.get("imo")
        if pd.notna(imo) and imo:
            try:
                imo_int = int(float(imo))
                result[imo_int] = {
                    "sdn_name": str(row.get("sdn_name", "")),
                    "sdn_program": str(row.get("sdn_program", "")),
                }
            except:
                pass
    print(f"[OFAC] {len(result)} 个 IMO")
    return result


# ============================================================
# 2. UN
# ============================================================

def load_un():
    un_xml = EXTERNAL / "UN-EU-UK 制裁名单" / "UN" / "consolidatedLegacyByPRN.xml"
    import xml.etree.ElementTree as ET
    tree = ET.parse(str(un_xml))
    root = tree.getroot()

    imos = {}
    for tag in ['ENTITY', 'INDIVIDUAL']:
        container = root.find('ENTITIES') if tag == 'ENTITY' else root.find('INDIVIDUALS')
        if container is None:
            continue
        for el in container.findall(tag):
            full = ' '.join(sub.text or '' for sub in el)
            ref = el.findtext('REFERENCE_NUMBER', '') or ''
            list_type = el.findtext('UN_LIST_TYPE', '') or ''
            name = el.findtext('FIRST_NAME', '') or el.findtext('SECOND_NAME', '') or ''
            for imo in extract_imos(full):
                if imo not in imos:
                    imos[imo] = f"UN:{list_type}/{ref}"
    print(f"[UN] {len(imos)} IMO")
    return imos


# ============================================================
# 3. EU
# ============================================================

def load_eu():
    eu_xlsx = EXTERNAL / "UN-EU-UK 制裁名单" / "EU" / "EU+designated+vessels+consolidated.xlsx"
    df = pd.read_excel(str(eu_xlsx))
    df = df.dropna(subset=['IMO number'])
    df['IMO number'] = df['IMO number'].astype(int)
    imos = {}
    for _, row in df.iterrows():
        imo = int(row['IMO number'])
        name = str(row.get('Vessel name at designation time', ''))
        date = str(row.get('Date of application', ''))
        imos[imo] = f"EU:{name} ({date})"
    print(f"[EU] {len(imos)} IMO")
    return imos


# ============================================================
# 4. UK
# ============================================================

def load_uk():
    uk_csv = EXTERNAL / "UN-EU-UK 制裁名单" / "UK" / "UK-Sanctions-List.csv"
    with open(uk_csv, 'r', encoding='utf-8', errors='replace') as f:
        lines = [l for l in f if l.strip() and not l.strip().startswith('Report Date')]

    df = pd.read_csv(StringIO('\n'.join(lines)), low_memory=False, on_bad_lines='skip')

    imos = {}
    if 'IMO number' in df.columns:
        for _, row in df.iterrows():
            val = str(row.get('IMO number', ''))
            m = re.search(r'(\d{7})', val)
            if m:
                imo = int(m.group(1))
                if imo not in imos:
                    regime = str(row.get('Regime', '')) if 'Regime' in df.columns else ''
                    name = str(row.get('Name 6', '')) or str(row.get('Name 1', ''))
                    ship_type = str(row.get('Type of ship', ''))
                    flag = str(row.get('Current believed flag of ship', ''))
                    imos[imo] = f"UK:{name} [{regime}] ({ship_type}, {flag})"
    print(f"[UK] {len(imos)} IMO")
    return imos


# ============================================================
# 5. 构建输出矩阵
# ============================================================

def build_matrix():
    print("\n[加载制裁名单]")
    ofac = load_ofac()
    un = load_un()
    eu = load_eu()
    uk = load_uk()

    print("\n[构建待匹配列表]")
    archive = get_ship_archive()
    ships = archive._df
    ais_mmsi = set(get_all_mmsi())
    archive_mmsi = archive.get_mmsi_set()
    ais_only = ais_mmsi - archive_mmsi

    records = []

    # 有档案的船
    for _, row in ships.iterrows():
        mmsi = row.get("ship_mmsi")
        imo_raw = str(row.get("ship_imo", ""))
        imo_match = re.search(r'\b(\d{7})\b', imo_raw)
        imo_int = int(imo_match.group(1)) if imo_match else None

        records.append(build_row(
            mmsi=int(mmsi) if pd.notna(mmsi) else None,
            imo=imo_int,
            name=str(row.get("ship_name", "")).strip(),
            country=str(row.get("ship_country_name", "")).strip(),
            operator=str(row.get("operator_name", "")).strip(),
            build_year=row.get("ship_build_year"),
            ship_type=str(row.get("ship_type", "")).strip(),
            deadweight=row.get("ship_dead"),
            source="archive",
            ofac=ofac, un=un, eu=eu, uk=uk,
        ))

    # AIS独有
    for mmsi in sorted(ais_only):
        records.append(build_row(
            mmsi=mmsi, imo=None, name="", country="", operator="",
            build_year=None, ship_type="", deadweight=None, source="ais_only",
            ofac=ofac, un=un, eu=eu, uk=uk,
        ))

    df = pd.DataFrame(records)

    # 来源计数
    df["sanction_sources"] = (
        df["hit_ofac"].astype(int) +
        df["hit_un"].astype(int) +
        df["hit_eu"].astype(int) +
        df["hit_uk"].astype(int)
    )

    # 风险等级
    def classify(row):
        if row["sanction_sources"] >= 3:
            return "高风险"
        elif row["sanction_sources"] >= 2:
            return "中风险"
        elif row["sanction_sources"] >= 1:
            return "低风险"
        return "未命中"

    df["risk_level"] = df.apply(classify, axis=1)

    return df


def build_row(mmsi, imo, name, country, operator, build_year, ship_type, deadweight, source,
              ofac, un, eu, uk):
    hit_ofac = imo in ofac if imo else False
    hit_un = imo in un if imo else False
    hit_eu = imo in eu if imo else False
    hit_uk = imo in uk if imo else False

    detail_parts = []
    if hit_ofac:
        detail_parts.append(f"[OFAC] {ofac[imo].get('sdn_program','')}")
    if hit_un:
        detail_parts.append(f"[UN] {un[imo]}")
    if hit_eu:
        detail_parts.append(f"[EU] {eu[imo]}")
    if hit_uk:
        detail_parts.append(f"[UK] {uk[imo]}")

    return {
        "mmsi": mmsi,
        "imo": imo,
        "ship_name": name,
        "country": country,
        "operator": operator,
        "build_year": build_year,
        "ship_type": ship_type,
        "deadweight": deadweight,
        "source": source,
        "hit_ofac": hit_ofac,
        "hit_un": hit_un,
        "hit_eu": hit_eu,
        "hit_uk": hit_uk,
        "sanction_detail": " | ".join(detail_parts) if detail_parts else "",
    }


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    t0 = time.time()
    print("=" * 60)
    print("四合一制裁筛查（OFAC + UN + EU + UK）")
    print("=" * 60)

    df = build_matrix()

    # 保存
    output_path = OUTPUT / "sanctions_matrix.csv"
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"\n[保存] {output_path} ({time.time()-t0:.1f}s)")

    # 摘要
    total = len(df)
    hit_any = (df["sanction_sources"] > 0).sum()
    print(f"\n{'='*60}")
    print(f"总船只: {total}")
    print(f"命中任一制裁: {hit_any} ({hit_any/total*100:.1f}%)")
    print(f"\n来源分布:")
    for s in [4, 3, 2, 1, 0]:
        cnt = (df["sanction_sources"] == s).sum()
        print(f"  {s}个来源: {cnt} ({cnt/total*100:.1f}%)")

    print(f"\n各来源命中:")
    for label, col in [("OFAC", "hit_ofac"), ("UN", "hit_un"), ("EU", "hit_eu"), ("UK", "hit_uk")]:
        cnt = df[col].sum()
        print(f"  {label}: {int(cnt)}")

    print(f"\n风险分级:")
    for level in ["高风险", "中风险", "低风险", "未命中"]:
        cnt = (df["risk_level"] == level).sum()
        print(f"  {level}: {cnt} ({cnt/total*100:.1f}%)")

    print("\n完成")
