import heapq

H, W, T = map(int, input().split())
grid = [input() for _ in range(H)]

# スタートとゴールを探す
for i in range(H):
    for j in range(W):
        if grid[i][j] == 'S':
            sx, sy = i, j
        if grid[i][j] == 'G':
            gx, gy = i, j

dx = [1, -1, 0, 0]
dy = [0, 0, 1, -1]

# 判定関数
def can(x):
    INF = 10**18
    dist = [[INF]*W for _ in range(H)]
    dist[sx][sy] = 0

    pq = [(0, sx, sy)]

    while pq:
        cost, x0, y0 = heapq.heappop(pq)

        if cost > dist[x0][y0]:
            continue

        for d in range(4):
            nx = x0 + dx[d]
            ny = y0 + dy[d]

            if 0 <= nx < H and 0 <= ny < W:

                if grid[nx][ny] == '#':
                    ncost = cost + x
                else:
                    ncost = cost + 1

                if ncost < dist[nx][ny]:
                    dist[nx][ny] = ncost
                    heapq.heappush(pq, (ncost, nx, ny))

    return dist[gx][gy] <= T


# 二分探索
left = 1
right = 10**9
answer = 1

while left <= right:
    mid = (left + right) // 2

    if can(mid):
        answer = mid
        left = mid + 1
    else:
        right = mid - 1

print(answer)