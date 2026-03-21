import numpy as np
from itertools import combinations


def solve_color_grid(top_green, left_green, bottom_yellow, right_yellow, initial_grid=None):
    n, m = len(left_green), len(top_green)
    if initial_grid is None:
        initial_grid = [[0] * m for _ in range(n)]
    initial_grid = np.array(initial_grid)

    def get_possible_grids(row_counts, col_counts, n, m, value, initial):
        forced_must, forced_zero = set(), set()

        for i in range(n):
            for j in range(m):
                if initial[i][j] == value:
                    forced_must.add((i, j))
                elif initial[i][j] in [1, 2, -1]:
                    forced_zero.add((i, j))

        for i in range(n):
            must_in_row = len([j for j in range(m) if (i, j) in forced_must])
            zero_in_row = len([j for j in range(m) if (i, j) in forced_zero])
            if must_in_row > row_counts[i] or m - zero_in_row < row_counts[i]:
                return []

        for j in range(m):
            must_in_col = len([i for i in range(n) if (i, j) in forced_must])
            zero_in_col = len([i for i in range(n) if (i, j) in forced_zero])
            if must_in_col > col_counts[j] or n - zero_in_col < col_counts[j]:
                return []

        row_poss, valid_grids = [], []

        for i in range(n):
            need_count = row_counts[i] - len([j for j in range(m) if (i, j) in forced_must])
            available = [j for j in range(m) if (i, j) not in forced_must and (i, j) not in forced_zero]
            if need_count < 0 or need_count > len(available):
                return []
            row_poss.append(list(combinations(available, need_count)))

        def build_grid(row_idx, current_grid):
            if row_idx == n:
                for col in range(m):
                    if sum(current_grid[row][col] for row in range(n)) != value * col_counts[col]:
                        return
                valid_grids.append([row[:] for row in current_grid])
                return

            for poss in row_poss[row_idx]:
                new_grid = [row[:] for row in current_grid]
                for j in range(m):
                    new_grid[row_idx][j] = value if (row_idx, j) in forced_must else 0
                for col in poss:
                    new_grid[row_idx][col] = value
                build_grid(row_idx + 1, new_grid)

        build_grid(0, [[0] * m for _ in range(n)])
        return valid_grids

    green_grids = get_possible_grids(left_green, top_green, n, m, 1, initial_grid)
    yellow_grids = get_possible_grids(right_yellow, bottom_yellow, n, m, 2, initial_grid)

    print(f"绿色图可能数量: {len(green_grids)}")
    print(f"黄色图可能数量: {len(yellow_grids)}")

    def get_determined_cells(grids, value):
        determined = set()
        for i in range(n):
            for j in range(m):
                values = set(grid[i][j] for grid in grids)
                if len(values) == 1 and values.pop() == value:
                    determined.add((i, j))
        return determined

    green_determined = get_determined_cells(green_grids, 1)
    yellow_determined = get_determined_cells(yellow_grids, 2)

    print(f"确定绿的格子: {green_determined if green_determined else '无'}")
    print(f"确定黄的格子: {yellow_determined if yellow_determined else '无'}")

    forced = [[0] * m for _ in range(n)]
    conflict_cells = green_determined & yellow_determined
    for (i, j) in green_determined:
        forced[i][j] = 1
    for (i, j) in yellow_determined:
        forced[i][j] = 2
    if conflict_cells:
        print(f"\n❌ 存在确定性冲突！冲突格子: {conflict_cells}")
        for (i, j) in conflict_cells:
            forced[i][j] = 3
        return np.array(forced), None

    valid_solutions = []
    [[valid_solutions.append([[g_grid[i][j] or y_grid[i][j] for j in range(m)] for i in range(n)]) if all(
        not ((g_grid[i][j] == 1 and y_grid[i][j] == 2) or (forced[i][j] == 1 and g_grid[i][j] != 1) or
             (forced[i][j] == 2 and y_grid[i][j] != 2)) for i in range(n) for j in range(m)) else 0
        for y_grid in yellow_grids] for g_grid in green_grids]

    print(f"\n✅ 找到 {len(valid_solutions)} 个有效组合解")
    return np.array(forced), valid_solutions


def print_grid_formatted(grid, constraint, title):
    n, m = grid.shape
    cell_symbol = ["·", "G", "Y", "X"]
    top, left, bottom, right = constraint
    print(f"\n{'=' * 50}\n【{title}】\n{'=' * 50}")
    print("    " + " ".join(f"{str(x):^{3}}" for x in top) + "\n")
    for i in range(n):
        row_content = " ".join(f"{cell_symbol[grid[i][j]]:^{3}}" for j in range(m))
        print(f"{f'{left[i]} │'} {row_content} {f'│ {right[i]}'}")
        print(f"  ├{'─' * (m * (3 + 1) + 1)}┤") if i < n - 1 else 0
    print("\n    " + " ".join(f"{str(x):^{3}}" for x in bottom))
    print(f"\n图例: ·=空白(0)  G=绿色(1)  Y=黄色(2)  X=冲突/红色(3)")


def print_solutions(solutions):
    if not solutions:
        return print(f"\n❌ 当前状态无解！")
    print(f"\n{'=' * 50}" + f"【所有可能的解】共 {len(solutions)} 个" + f"{'=' * 50}")
    cell_symbol = ["·", "G", "Y", "X"]
    for idx, sol in enumerate(solutions):
        n, m = len(sol), len(sol[0])
        print(f"\n方案 {idx + 1}:\n" + "  ┌" + "─" * (m * 4 + 1) + "┐")
        for i in range(n):
            row_str = " ".join(f"{cell_symbol[sol[i][j]]:^{3}}" for j in range(m))
            print(f"  │ {row_str} │")
        print("  └" + "─" * (m * 4 + 1) + "┘")
    print(f"\n图例: ·=空白(0)  G=绿色(1)  Y=黄色(2)")


def print_all_grids(forced, solutions, top_green, left_green, bottom_yellow, right_yellow):
    constraint = [top_green, left_green, bottom_yellow, right_yellow]
    print_grid_formatted(forced, constraint, "强制约束（确定性格子）")
    print_solutions(solutions)


if __name__ == "__main__":
    # 示例1：分离区域（唯一解）
    print("=" * 50 + "\n" + "示例1：分离区域（无冲突，唯一解）" + "\n" + "=" * 50)

    top1, left1 = [2, 2, 0, 0], [2, 2, 0, 0]
    bottom1, right1 = [0, 0, 2, 2], [0, 0, 2, 2]

    forced1, sols1 = solve_color_grid(top1, left1, bottom1, right1)
    print_all_grids(forced1, sols1, top1, left1, bottom1, right1)

    # 示例2：确定性冲突（无解）- 显示确定性格子+冲突
    print("=" * 50 + "\n" + "示例2：确定性冲突（显示确定性格子和冲突）" + "\n" + "=" * 50)

    top2, left2 = [2, 2, 0, 0], [2, 2, 0, 0]
    bottom2, right2 = [0, 2, 2, 0], [0, 2, 2, 0]

    forced2, sols2 = solve_color_grid(top2, left2, bottom2, right2)
    print_all_grids(forced2, sols2, top2, left2, bottom2, right2)

    # 示例3：双方多解，组合后多解
    print("=" * 50 + "\n" + "示例3：双方多解，组合后多解" + "\n" + "=" * 50)

    top3, left3 = [1, 1, 0], [1, 1, 0]
    bottom3, right3 = [0, 1, 1], [0, 1, 1]

    forced3, sols3 = solve_color_grid(top3, left3, bottom3, right3)
    print_all_grids(forced3, sols3, top3, left3, bottom3, right3)

    # 示例4：带初始预设，禁格用-1
    print("=" * 50 + "\n" + "示例4：带初始预设，禁格用-1" + "\n" + "=" * 50)

    initial4 = [
        [1, 1, 0, 0],
        [1, 1, 0, 0],
        [0, 0, -1, 0],
        [0, 0, 0, 0]
    ]

    top4, left4 = [2, 2, 0, 0], [2, 2, 0, 0]
    bottom4, right4 = [0, 0, 2, 2], [0, 0, 2, 2]

    forced4, sols4 = solve_color_grid(top4, left4, bottom4, right4, initial4)
    print_all_grids(forced4, sols4, top4, left4, bottom4, right4)

    # 示例5：初始预设限制单解
    print("=" * 50 + "\n" + "示例5：初始预设限制单解" + "\n" + "=" * 50)

    initial5 = [
        [1, 0, 0],
        [0, 0, 0],
        [0, 0, 0]
    ]

    top5, left5 = [1, 1, 0], [1, 1, 0]
    bottom5, right5 = [0, 1, 1], [0, 1, 1]

    forced5, sols5 = solve_color_grid(top5, left5, bottom5, right5, initial5)
    print_all_grids(forced5, sols5, top5, left5, bottom5, right5)
    