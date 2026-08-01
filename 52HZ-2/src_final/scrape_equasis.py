"""
Equasis 自动化查询 — 全量677艘, 断点续跑
"""
import time, csv, sys, os, os
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent.parent / "src_final"))
import pandas as pd
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

EMAIL = "eto24865@gmail.com"
PASSWORD = "5201314@Aa"

ROOT = Path(__file__).parent.parent
OUTPUT = ROOT / "output_final"

# 命令行参数: --start N  从第N行开始
start_idx = 0
for arg in sys.argv:
    if arg.startswith('--start='):
        start_idx = int(arg.split('=')[1])
        break

batch_label = f"_{start_idx}" if start_idx > 0 else ""
CSV_PATH = OUTPUT / f"equasis_company_changes{batch_label}.csv"

# 读取 IMO 列表（全量）
df = pd.read_csv(OUTPUT / "vessel_risk_profile.csv")
imos_all = df['imo'].dropna().unique()
imos_all = [str(int(float(i))) for i in imos_all if str(i).strip() and str(i).strip() != 'nan']

# 从 start_idx 开始, 每个批次取200条
total = len(imos_all)
imos = imos_all[start_idx:]
if start_idx == 0:
    end_idx = min(200, total)
    imos = imos[:200]
elif len(imos) > 200:
    imos = imos[:200]  # 每批200条
print(f"批次: start={start_idx}, 范围 [{start_idx+1}-{start_idx+len(imos)}] / {total}")

# 断点续跑
done = set()
if CSV_PATH.exists():
    done_df = pd.read_csv(CSV_PATH)
    done = set(done_df['imo'].astype(str))
imos = [i for i in imos if i not in done]
print(f"待查询: {len(imos)} 艘 (已跳过 {len(done)} 艘)")

if not imos:
    print("全部已完成!")
    exit(0)

# 浏览器
from selenium.webdriver.edge.options import Options as EdgeOptions
opts = EdgeOptions()
opts.add_argument('--proxy-server=http://127.0.0.1:7890')
opts.add_argument('--ignore-certificate-errors')
driver = webdriver.Edge(options=opts)
wait = WebDriverWait(driver, 15)
print("  使用 Edge + 代理")

try:
    # 登录
    print("\n[1] 登录...")
    driver.get("https://www.equasis.org/EquasisWeb/public/HomePage?fs=HomePage")
    time.sleep(5)
    e = wait.until(EC.presence_of_element_located((By.NAME, "j_email")))
    p = driver.find_element(By.NAME, "j_password")
    driver.execute_script("arguments[0].value = arguments[1]", e, EMAIL)
    driver.execute_script("arguments[0].value = arguments[1]", p, PASSWORD)
    driver.execute_script("arguments[0].click()", driver.find_element(By.NAME, "submit"))
    time.sleep(5)
    print(f"  登录完成: {driver.title}")

    # 逐船查询
    f = open(CSV_PATH, 'a', newline='', encoding='utf-8-sig')
    writer = csv.DictWriter(f, fieldnames=['imo','company_count','error'])
    if not CSV_PATH.exists() or os.path.getsize(CSV_PATH) == 0:
        writer.writeheader()

    for idx, imo in enumerate(imos):
        print(f"\n[{idx+1}/{len(imos)}] IMO={imo}", end='', flush=True)
        try:
            driver.get("https://www.equasis.org/EquasisWeb/public/HomePage?fs=ShipHistory")
            time.sleep(2)
            
            search = wait.until(EC.presence_of_element_located((By.ID, "P_ENTREE_HOME")))
            search.clear()
            search.send_keys(imo + Keys.RETURN)
            time.sleep(3)
            
            try:
                first = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "#ShipResultId a")))
                first.click()
                time.sleep(3)
            except:
                print("  无结果,跳过")
                row = {"imo": imo, "company_count": 0, "error": "no_result"}
                writer.writerow(row); f.flush()
                continue
            
            # Ship History 按钮（先点它，Company 才出现）
            try:
                sh_btn = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(),'Ship History')]")))
                driver.execute_script("arguments[0].click()", sh_btn)
                time.sleep(3)
            except:
                pass
            
            # Company 展开
            try:
                ch = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//h3[contains(text(),'Company')]")))
                driver.execute_script("arguments[0].click()", ch)
                time.sleep(2)
            except:
                pass
            
            entries = driver.find_elements(By.CSS_SELECTOR, 
                "div.blocLSMobile.col-xs-12.col-sm-12.no-padding")
            count = len(entries)
            print(f"  {count}条")
            row = {"imo": imo, "company_count": count, "error": ""}
            writer.writerow(row); f.flush()
            time.sleep(1)
            
        except Exception as ex:
            print(f"  出错: {ex}")
            row = {"imo": imo, "company_count": 0, "error": str(ex)[:80]}
            writer.writerow(row); f.flush()
            time.sleep(3)

    f.close()
finally:
    driver.quit()

print(f"\n完成: {CSV_PATH}")
