import zipfile
from chardet import detect  # 需要安装：pip install chardet


def detect_zip_encoding(zip_path):
    """检测ZIP文件使用的文件名编码"""
    with zipfile.ZipFile(zip_path, 'r') as zf:
        # 获取前10个文件名样本（可根据需要调整）
        samples = [info.filename for info in zf.infolist()[:150]]

        # 方法1：使用chardet自动检测
        raw_bytes = b''.join(s.encode('cp437') for s in samples)
        detection = detect(raw_bytes)
        auto_encoding = detection['encoding']

        # 方法2：常见编码测试
        test_encodings = [
            'utf-8',
            'gbk',
            'gb2312',
            'gb18030',
            'big5',
            'shift_jis',
            'cp932',
            'euc-jp',
            'euc-kr',
            'iso-8859-1'
        ]

        # 评估可读性
        viable_encodings = []
        for enc in test_encodings:
            try:
                decoded = [s.encode('cp437').decode(enc) for s in samples]
                # 简单中文检测（Unicode范围）
                if any('\u4e00' <= c <= '\u9fff' for name in decoded for c in name):
                    viable_encodings.append(enc)
            except:
                continue

        # 组合结果
        return {
            'detected_encoding': auto_encoding,
            'possible_encodings': list(set(viable_encodings + [auto_encoding]))
        }


# 使用示例
encoding_info = detect_zip_encoding("output/DeskpetETO.zip")
print(f"自动检测编码: {encoding_info['detected_encoding']}")
print(f"可能适用的编码: {encoding_info['possible_encodings']}")
