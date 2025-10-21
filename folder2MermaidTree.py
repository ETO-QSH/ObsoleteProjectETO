import re
import base64
import hashlib
import urllib.request
from pathlib import Path
from typing import List, Tuple, Optional, Set


def _scan(
    root: Path, max_d: int, cur: int = 0, base: Optional[Path] = None,
    exclude_set: Optional[Set[Path]] = None
) -> Tuple[List[Tuple[Path, int, bool]], int, int]:

    if base is None:
        base = root
    if exclude_set is None:
        exclude_set = set()

    if max_d != -1 and cur >= max_d:
        return [], 0, 0
    dirs = files = 0
    out: List[Tuple[Path, int, bool]] = []

    try:
        for p in sorted(root.iterdir(), key=lambda x: (x.is_file(), x.name)):
            p_res = p.resolve()
            if p_res in exclude_set:
                continue

            is_dir = p.is_dir()
            out.append((p_res, cur, is_dir))
            if is_dir:
                dirs += 1
                sub_list, sub_d, sub_f = _scan(p, max_d, cur + 1, base=base, exclude_set=exclude_set)
                out.extend(sub_list)
                dirs += sub_d
                files += sub_f
            else:
                files += 1

    except PermissionError:
        pass
    return out, dirs, files


def _escape(name: str, standard: bool) -> str:
    if not standard:
        name = name.replace('“', "'").replace('”', "'").replace('"', "'")
        name = name.replace('(', '（').replace(')', '）')
        return name
    else:
        return name.replace('"', '&quot;')


def _node_id(path: Path) -> str:
    safe = re.sub(r'\W+', '_', path.name)
    h = hashlib.md5(str(path).encode()).hexdigest()[:6]
    return f'{safe}_{h}'


def folder_to_png(folder_path: str, max_depth: int = -1, exclude: Optional[List[str]] = None, standard: bool = False) -> str:
    root = Path(folder_path).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f'{folder_path} 不是有效目录')

    exclude_abs: Set[Path] = set()
    if exclude:
        for rel in exclude:
            try:
                p = (root / Path(rel)).resolve()
            except Exception:
                p = (root / Path(rel)).absolute()
            exclude_abs.add(p)

    items, dir_cnt, file_cnt = _scan(root, max_depth, 0, base=root, exclude_set=exclude_abs)
    root_id = _node_id(root)
    edges = set()

    lines = [
        f'%% 文件夹：{dir_cnt} 个，文件：{file_cnt} 个', 'graph LR',
        f'    {root_id}@{{{{ shape: "procs", label: "{_escape(root.name, standard)}" }}}}'
        if standard else f'    {root_id}[( {_escape(root.name, standard)} )]'
    ]

    for p, depth, is_dir in items:
        pid = _node_id(p)
        if not standard:
            label = _escape(p.name, standard)
            lines.append(f'    {pid}[[{label}]]' if is_dir else f'    {pid}([{label}])')
        else:
            shape = 'win-pane' if is_dir else 'rounded'
            lines.append(f'    {pid}@{{{{ shape: "{shape}", label: "{_escape(p.name)}" }}}}')

        parent_id = root_id if depth == 0 else _node_id(p.parent)
        edge = (parent_id, pid)
        if edge not in edges:
            edges.add(edge)
            lines.append(f'    {parent_id} --> {pid}')

    mermaid_src = '\n'.join(lines)

    png_path = root.with_suffix('.png')
    b64 = base64.b64encode(mermaid_src.encode()).decode()
    url = f'https://mermaid.ink/img/{b64}?theme=base&bgColor=white'

    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            png_path.write_bytes(resp.read())
    except Exception as e:
        print(f'[WARN] PNG 生成失败（{e}），仅返回 Mermaid 源码')

    return mermaid_src


if __name__ == '__main__':
    excludes = ['.git', '.idea', '.venv', '~$2Hz杯”2025届海事编程马拉松大赛决赛题目.docx']
    print(folder_to_png(r'./', exclude=excludes))
