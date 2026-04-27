from collections import deque

H, W = map(int, input().split())
start = None
goal = None
grid = []
for i in range(H):
    row = list(input().strip())
    if "S" in row:
        start = (i, row.index("S"))
    if "G" in row:
        goal = (i, row.index("G"))
    grid.append(row)

## 方針
## SからGまで到達可能かを求め、到達可能な場合は経路を求める
## 経路は幅優先探索で求める
## #には立ち入ることができない
## oは直前の移動と同じ方向に移動しなければならない
## xは直前の移動と同じ方向に移動できない
## 出力経路の例は、DRUUDDRRのように、Dは下、Rは右、Uは上、Lは左を表す

DIRS = [
    (0, 1, "R"),
    (0, -1, "L"),
    (1, 0, "D"),
    (-1, 0, "U"),
]
NO_DIR = 4

def can_move(cell, prev_dir, next_dir):
    if cell == "o" and prev_dir != NO_DIR and prev_dir != next_dir:
        return False
    if cell == "x" and prev_dir != NO_DIR and prev_dir == next_dir:
        return False
    return True


def bfs(start, goal):
    start_state = (start[0], start[1], NO_DIR)
    queue = deque([start_state])
    visited = [[[False] * 5 for _ in range(W)] for _ in range(H)]
    visited[start[0]][start[1]][NO_DIR] = True
    ## parentを使って、経路を復元する
    parent = [[[-1] * 5 for _ in range(W)] for _ in range(H)]

    while queue:
        x, y, prev_dir = queue.popleft()
        if (x, y) == goal:
            path = []
            current_x = x
            current_y = y
            current_dir = prev_dir
            while current_dir != NO_DIR:
                dx, dy, move = DIRS[current_dir]
                path.append(move)
                parent_dir = parent[current_x][current_y][current_dir]
                current_x -= dx
                current_y -= dy
                current_dir = parent_dir
            path.reverse()
            return "".join(path)

        for next_dir, (dx, dy, _) in enumerate(DIRS):
            ## 移動不可能ならスキップする
            if not can_move(grid[x][y], prev_dir, next_dir):
                continue

            nx = x + dx
            ny = y + dy

            if not (0 <= nx < H and 0 <= ny < W):
                continue
            if grid[nx][ny] == "#":
                continue
            if visited[nx][ny][next_dir]:
                continue

            visited[nx][ny][next_dir] = True
            parent[nx][ny][next_dir] = prev_dir
            queue.append((nx, ny, next_dir))

    return None


path = bfs(start, goal)

if path is None:
    print("No")
else:
    print("Yes")
    print(path)
