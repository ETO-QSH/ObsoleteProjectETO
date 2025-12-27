import os
import json
from datetime import datetime
from functools import partial


def _log(msg, log_file):
    timestamp = datetime.now().strftime('%Y/%m/%d %H-%M-%S')
    msg = f"[{timestamp}] {msg}"
    log_file.write(f"{msg}\n")
    log_file.flush()
    print(msg)


def load_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # 获取项目根目录

config_path = os.path.join(project_root, 'config.json')
config = load_config(config_path)

adb_path = config['adb_path']
sleep_time = config['sleep_time']

screenshot_dir = os.path.abspath(os.path.join(project_root, config['screenshot_dir']))
picture_dir = os.path.abspath(os.path.join(project_root, config['picture_dir']))

log_path = os.path.join(project_root, config['log_file'])
log_file = open(log_path, 'a', encoding='utf-8')

log = partial(_log, log_file=log_file)

ocr_pic = {
    "黍": "黍.png",
    "年": "年.png",
    "令": "令.png",
    "钱盒": "钱盒.png",
    "收起": "收起.png",
    "收下": "收下.png",
    "退出": "退出.png",
    "小常乐": "小常乐.png",
    "衡如常": "衡如常.png",
    "厉如锋": "厉如锋.png",
    "花如簇": "花如簇.png",
    "来就来": "来就来.png",
    "重新投钱": "重新投钱.png",
    "还是算了": "还是算了.png",
    "投钱确认": "投钱确认.png",
    "前往出发": "前往出发.png",
    "欣然应许": "欣然应许.png",
    "要书一卷": "要书一卷.png",
    "要酒一壶": "要酒一壶.png",
    "要兵器一对": "要兵器一对.png",
    "确定这么做": "确定这么做.png",
    "事件结束确认": "事件结束确认.png",
    "投钱结束确认": "投钱结束确认.png",
    "剩余烛火": ("剩余烛火.png", [75, 60, 150, 135]),
    "收藏品": ("收藏品.png", [50, 15, 90, 60]),
    "源石锭": ("源石锭.png", [90, 25, 190, 65]),
    "票券": ("票券.png", [90, 25, 190, 65])
}
