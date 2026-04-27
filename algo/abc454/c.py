from collections import deque


N, M = map(int, input().split())

graph = [[] for _ in range(N + 1)]
for _ in range(M):
    a, b = map(int, input().split())
    graph[a].append(b)

visited = [False] * (N + 1)
visited[1] = True

queue = deque([1])

while queue:
    item = queue.popleft()
    for next_item in graph[item]:
        if visited[next_item]:
            continue
        visited[next_item] = True
        queue.append(next_item)

print(sum(visited))
