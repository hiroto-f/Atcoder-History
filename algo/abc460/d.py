from collections import deque


H, W = map(int, input().split())
S = [input() for _ in range(H)]

DIR = [
    (-1, -1),
    (-1, 0),
    (-1, 1),
    (0, -1),
    (0, 1),
    (1, -1),
    (1, 0),
    (1, 1),
]

dist = [[-1] * W for _ in range(H)]
que = deque()

for i in range(H):
    for j in range(W):
        if S[i][j] == ".":
            continue

        for di, dj in DIR:
            ni = i + di
            nj = j + dj

            if 0 <= ni < H and 0 <= nj < W and S[ni][nj] == ".":
                dist[i][j] = 0
                que.append((i, j))
                break

while que:
    i, j = que.popleft()

    for di, dj in DIR:
        ni = i + di
        nj = j + dj

        if 0 <= ni < H and 0 <= nj < W and dist[ni][nj] == -1:
            dist[ni][nj] = dist[i][j] + 1
            ## 新たに起点に追加する
            que.append((ni, nj))

ans = [["."] * W for _ in range(H)]

for i in range(H):
    for j in range(W):
        if dist[i][j] != -1 and dist[i][j] % 2 == 0:
            ans[i][j] = "#"

for row in ans:
    print("".join(row))
