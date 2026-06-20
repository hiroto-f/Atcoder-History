n, m, y = map(int, input().split())

warp = n
## n番目はワープを表すノード
graph = [[] for _ in range(n + 1)]

for i in range(m):
    u, v, t = map(int, input().split())
    graph[u - 1].append((v - 1, t))
    graph[v - 1].append((u - 1, t))

## ワープの辺を追加
x = list(map(int, input().split()))
for i in range(n):
    graph[i].append((warp, x[i] + y))
    graph[warp].append((i, x[i]))

## ダイクストラ法
import heapq

INF = 10**30
dist = [INF] * (n + 1)
dist[0] = 0

heap = [(0, 0)]

while heap:
    current_dist, current = heapq.heappop(heap)

    if dist[current] != current_dist:
        continue

    for next_node, cost in graph[current]:
        next_dist = current_dist + cost

        if next_dist < dist[next_node]:
            dist[next_node] = next_dist
            heapq.heappush(heap, (next_dist, next_node))

print(*dist[1:n])
