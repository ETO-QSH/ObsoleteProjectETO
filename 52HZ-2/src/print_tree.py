import os
import sys
from pathlib import Path


def print_directory_tree(root_dir, prefix="", is_last=True, max_depth=None, current_depth=0):
    if max_depth is not None and current_depth > max_depth:
        return

    dir_name = os.path.basename(root_dir)
    if not dir_name:
        dir_name = root_dir

    if current_depth == 0:
        print(dir_name + "/")
    else:
        connector = "└── " if is_last else "├── "
        print(prefix + connector + dir_name + "/")

    extension = "    " if is_last else "│   "
    next_prefix = prefix + extension

    try:
        items = os.listdir(root_dir)
    except PermissionError:
        print(next_prefix + "└── [权限不足，无法访问]")
        return
    except OSError:
        print(next_prefix + "└── [无法访问]")
        return

    dirs = []
    files = []

    for item in items:
        if item.startswith('.'):
            continue
        item_path = os.path.join(root_dir, item)
        if os.path.isdir(item_path):
            dirs.append(item)
        else:
            files.append(item)

    dirs.sort()
    files.sort()

    all_items = dirs + files

    for i, item in enumerate(all_items):
        item_path = os.path.join(root_dir, item)
        is_last_item = (i == len(all_items) - 1)

        if os.path.isdir(item_path):
            print_directory_tree(
                item_path,
                next_prefix,
                is_last_item,
                max_depth,
                current_depth + 1
            )
        else:
            connector = "└── " if is_last_item else "├── "
            print(next_prefix + connector + item)


def main():
    target_dir = sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent.parent
    print_directory_tree(target_dir)


if __name__ == "__main__":
    main()
