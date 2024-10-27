import os
import shutil
from datetime import datetime, timedelta


def copy_files_with_date(src_dir, dest_dir, target_date):
    # 确保目标目录存在，如果不存在则创建
    os.makedirs(dest_dir, exist_ok=True)

    # 遍历源目录
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            file_path = os.path.join(root, file)
            # 获取文件的修改时间
            file_mtime = os.path.getmtime(file_path)
            file_mtime_dt = datetime.fromtimestamp(file_mtime)

            # 检查文件的修改日期是否为目标日期
            if file_mtime_dt.date() == target_date:
                # 构造目标文件路径，保持原有的目录结构
                relative_path = os.path.relpath(root, src_dir)
                dest_file_path = os.path.join(dest_dir, relative_path, file)

                # 确保目标文件的目录存在
                os.makedirs(os.path.dirname(dest_file_path), exist_ok=True)

                # 复制文件
                shutil.copy2(file_path, dest_file_path)
                print(f"Copied '{file_path}' to '{dest_file_path}'")


# 使用示例
src_directory = 'Android'  # 源目录路径
dest_directory = 'ark-ETO'  # 目标目录路径
target_date = datetime(2024, 10, 23).date()  # 目标日期

copy_files_with_date(src_directory, dest_directory, target_date)
