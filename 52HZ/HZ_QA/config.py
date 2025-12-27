import os
from datetime import datetime
from functools import partial
from pathlib import Path


ROOT = Path(__file__).parent.parent
CELL_M = 1000  # 1 km
CORRIDOR_GEOJSON = ROOT / 'database/corridor/corridor.geojson'
OUT_PUT = Path("output")
OUT_PUT.mkdir(exist_ok=True)


def _log(msg, log_file):
    timestamp = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    msg = f"[{timestamp}] {msg}"
    log_file.write(f"{msg}\n")
    log_file.flush()
    print(msg)


def safe_exit(code):
    log("程序运行结束")
    log_file.close()
    exit(code)


log_path = os.path.join(ROOT, "HZ_QA/output/log.log")
log_file = open(log_path, 'a', encoding='utf-8')

log = partial(_log, log_file=log_file)
log("-" * 100)
