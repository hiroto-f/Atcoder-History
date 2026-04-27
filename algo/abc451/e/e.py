def main():
    n = int(input())

    dist = [[0] * n for _ in range(n)]
    for i in range(n - 1):
        row = list(map(int, input().split()))
        for offset, value in enumerate(row, start=1):
            j = i + offset
            dist[i][j] = value
            dist[j][i] = value

    inf = 10**18
    parent = [-1] * n
    min_cost = [inf] * n
    used = [False] * n
    min_cost[0] = 0

    ## Prim's algorithm
    for _ in range(n):
        v = -1
        best = inf
        for i in range(n):
            if not used[i] and min_cost[i] < best:
                best = min_cost[i]
                v = i

        used[v] = True
        row = dist[v]
        for u in range(n):
            if not used[u] and row[u] < min_cost[u]:
                min_cost[u] = row[u]
                parent[u] = v

    graph = [[] for _ in range(n)]
    for v in range(1, n):
        p = parent[v]
        w = dist[v][p]
        graph[v].append((p, w))
        graph[p].append((v, w))

    for start in range(n):
        stack = [(start, -1, 0)]
        while stack:
            v, prev, current = stack.pop()
            if current != dist[start][v]:
                print("No")
                return

            for to, weight in graph[v]:
                if to != prev:
                    stack.append((to, v, current + weight))

    print("Yes")


if __name__ == "__main__":
    main()
