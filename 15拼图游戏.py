import heapq


class PuzzleState:
    def __init__(self, board, moves=0, prev=None):
        self.board = board  # tuple of tuples
        self.moves = moves  # g(n)
        self.prev = prev    # 用于回溯路径
        self.n = len(board)
        self.zero_pos = self.find_zero()

    def find_zero(self):
        for i in range(self.n):
            for j in range(self.n):
                if self.board[i][j] == 0:
                    return i, j
        raise ValueError("No zero tile found")

    def manhattan_distance(self):
        distance = 0
        for i in range(self.n):
            for j in range(self.n):
                val = self.board[i][j]
                if val != 0:
                    target_x = (val - 1) // self.n
                    target_y = (val - 1) % self.n
                    distance += abs(i - target_x) + abs(j - target_y)
        return distance

    def f_score(self):
        return self.moves + self.manhattan_distance()

    def is_goal(self):
        expected = 1
        for i in range(self.n):
            for j in range(self.n):
                if i == self.n - 1 and j == self.n - 1:
                    if self.board[i][j] != 0:
                        return False
                else:
                    if self.board[i][j] != expected:
                        return False
                    expected += 1
        return True

    def neighbors(self):
        x, y = self.zero_pos
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.n and 0 <= ny < self.n:
                new_board = [list(row) for row in self.board]
                new_board[x][y], new_board[nx][ny] = new_board[nx][ny], new_board[x][y]
                yield PuzzleState(tuple(map(tuple, new_board)), self.moves + 1, self)

    def __lt__(self, other):
        return self.f_score() < other.f_score()

    def __hash__(self):
        return hash(self.board)

    def __eq__(self, other):
        return self.board == other.board


def solve_puzzle(initial_board):
    initial_state = PuzzleState(initial_board)
    if initial_state.is_goal():
        return []

    open_set = []
    heapq.heappush(open_set, initial_state)
    visited = set()
    visited.add(initial_state.board)

    while open_set:
        current = heapq.heappop(open_set)

        if current.is_goal():
            path = []
            while current.prev:
                path.append(current.board)
                current = current.prev
            return path[::-1]

        for neighbor in current.neighbors():
            if neighbor.board not in visited:
                visited.add(neighbor.board)
                heapq.heappush(open_set, neighbor)

    return None  # 无解


def is_solvable(board):
    """
    15-puzzle（行主序目标，右下角为 0）
    行号：从上往下，1-based（最顶行=1）
    """
    # 1. 忽略 0 的逆序数
    flat = [v for row in board for v in row if v != 0]
    inv = sum(1 for i, vi in enumerate(flat) for vj in flat[i + 1:] if vi > vj)

    # 2. 行号：从上往下 0-based
    zero_row = next(i for i, row in enumerate(board) if 0 in row)

    # 3. 判定
    return inv % 2 == 0 if len(board) % 2 == 1 else (inv - zero_row) % 2 == 1


if __name__ == "__main__":
    initial = (
        (12, 1, 2, 15),
        (11, 6, 5, 8),
        (7, 10, 9, 4),
        (0, 13, 14, 3)
    )

    if is_solvable(initial):
        solution = solve_puzzle(initial)
        print("共 {} 步：".format(len(solution)), end='')
        print(f"\n{'—' * 21}\n".join(("", *(f'| {" | ".join(f"{v:2d}" for v in row)} |' for row in initial), "")))

        for i, step in enumerate(solution, 1):
            print(f"第 {i} 步：")
            print(f"\n{'—' * 21}\n".join(("", *(f'| {" | ".join(f"{v:2d}" for v in row)} |' for row in step), "")))

    else:
        print("此题无解！")
