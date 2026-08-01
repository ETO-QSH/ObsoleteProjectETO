import zipfile
import pandas as pd
import geopandas as gpd
from pathlib import Path

EXTERNAL_DIR = Path("../external")
MAX_PREVIEW_ROWS = 3
MAX_COL_WIDTH = 60


def _apply_map(df, func):
    if hasattr(df, "map"):
        return df.map(func)
    return df.applymap(func)


def truncate(s, width=MAX_COL_WIDTH):
    if s is None:
        return "None"
    s = str(s)
    if len(s) > width:
        return s[:width - 3] + "..."
    return s


def print_separator(title=""):
    print("\n" + "=" * 70)
    if title:
        print(f"  {title}")
        print("=" * 70)


def scan_csv(path: Path):
    try:
        df = pd.read_csv(path, low_memory=False)
        print(f"  📄 文件: {path}")
        print(f"  📊 行数: {len(df):,}  |  列数: {len(df.columns)}")
        print(f"  📋 列名: {list(df.columns)}")
        if len(df) > 0:
            print(f"  🔍 前 {min(MAX_PREVIEW_ROWS, len(df))} 行:")
            preview = _apply_map(df.head(MAX_PREVIEW_ROWS), truncate)
            print(preview.to_string(index=False))
        else:
            print("  ⚠️  空文件")
        del df
    except Exception as e:
        print(f"  ❌ 读取失败: {e}")


def scan_excel(path: Path):
    try:
        xl = pd.ExcelFile(path)
        print(f"  📄 文件: {path}")
        print(f"  📑 Sheet 列表: {xl.sheet_names}")
        for sheet in xl.sheet_names:
            print(f"\n  ── Sheet: '{sheet}' ──")
            df = pd.read_excel(path, sheet_name=sheet, nrows=1000)
            print(f"    📊 行数: {len(df):,}  |  列数: {len(df.columns)}")
            print(f"    📋 列名: {list(df.columns)}")
            if len(df) > 0:
                print(f"    🔍 前 {min(MAX_PREVIEW_ROWS, len(df))} 行:")
                preview = _apply_map(df.head(MAX_PREVIEW_ROWS), truncate)
                lines = preview.to_string(index=False).split("\n")
                print("    " + "\n    ".join(lines))
            else:
                print("    ⚠️  空 Sheet")
            del df
        del xl
    except Exception as e:
        print(f"  ❌ 读取失败: {e}")


def scan_geojson(path: Path):
    if gpd is None:
        print(f"  ⚠️  geopandas 未安装，跳过 GeoJSON: {path}")
        return
    try:
        gdf = gpd.read_file(path)
        print(f"  📄 文件: {path}")
        print(f"  📊 要素数: {len(gdf):,}  |  属性列数: {len(gdf.columns) - 1}")  # 不含 geometry
        cols = [c for c in gdf.columns if c != "geometry"]
        print(f"  📋 属性列: {cols}")
        if len(gdf) > 0:
            print(f"  🔍 前 {min(MAX_PREVIEW_ROWS, len(gdf))} 行属性:")
            preview = _apply_map(gdf.head(MAX_PREVIEW_ROWS)[cols], truncate)
            print(preview.to_string(index=False))
            geom_types = gdf.geometry.type.value_counts().head(3).to_dict()
            print(f"  🗺️  Geometry 类型: {geom_types}")
        else:
            print("  ⚠️  空文件")
        del gdf
    except Exception as e:
        print(f"  ❌ 读取失败: {e}")


def scan_zip(path: Path):
    try:
        with zipfile.ZipFile(path, 'r') as zf:
            namelist = zf.namelist()
            print(f"  📄 文件: {path}")
            print(f"  📦 压缩包内文件数: {len(namelist)}")
            print(f"  📋 内容列表（前 20 个）:")
            for name in namelist[:20]:
                info = zf.getinfo(name)
                size = info.file_size
                print(f"    {name:50s}  ({size:>12,} bytes)")
            if len(namelist) > 20:
                print(f"    ... 等共 {len(namelist)} 个文件")
    except Exception as e:
        print(f"  ❌ 读取失败: {e}")


def scan_directory(dir_path: Path, depth=0):
    if not dir_path.exists():
        print(f"  ⚠️  目录不存在: {dir_path}")
        return

    indent = "  " * depth
    items = sorted(dir_path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))

    for item in items:
        if item.is_dir():
            print(f"\n{indent}📁 {item.name}/")
            scan_directory(item, depth + 1)
        elif item.is_file():
            suffix = item.suffix.lower()
            print(f"\n{indent}📄 {item.name}")

            if suffix == ".csv":
                scan_csv(item)
            elif suffix in (".xlsx", ".xls"):
                scan_excel(item)
            elif suffix == ".geojson":
                scan_geojson(item)
            elif suffix == ".zip":
                scan_zip(item)
            elif suffix in (".md", ".txt", ".json"):
                try:
                    with open(item, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()[:10]
                    print(f"  📄 文件: {item}")
                    print(f"  📊 总行数: {len(lines):,}")
                    print(f"  🔍 前 10 行:")
                    for i, line in enumerate(lines, 1):
                        print(f"    {i:2d}: {line.rstrip()}")
                except Exception as e:
                    print(f"  ❌ 读取失败: {e}")
            else:
                size = item.stat().st_size
                print(f"  📄 文件: {item}  ({size:,.0f} bytes) — 未识别格式，跳过")


if __name__ == "__main__":
    print("=" * 70)
    print("  External 外源数据扫描脚本")
    print("  扫描目录: {}".format(EXTERNAL_DIR.resolve()))
    print("=" * 70)

    if not EXTERNAL_DIR.exists():
        print(f"\n❌ 错误: 目录不存在 {EXTERNAL_DIR}")
        print("请确认脚本运行路径正确，或修改 EXTERNAL_DIR 变量。")
        exit(1)

    scan_directory(EXTERNAL_DIR)

    print("\n" + "=" * 70)
    print("  扫描完成")
    print("=" * 70)
