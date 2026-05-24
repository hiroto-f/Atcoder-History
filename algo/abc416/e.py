n, m = map(int, input().split())

## optimized_ways[i][j] は、i 街から j 街までの最適な移動時間
optimized_ways_by_car = [[float("inf")] * n for _ in range(n)]
print(optimized_ways_by_car)

for i in range(m):
    a, b, c = map(int, input().split())
    optimized_ways_by_car[a - 1][b - 1] = c
    optimized_ways_by_car[b - 1][a - 1] = c

k, t = map(int, input().split())
airports = set(map(int, input().split()))

q = int(input())

for _ in range(q):
    ans = 0
    query = list(map(int, input().split()))
    if query[0] == 1:
        _, x, y, t = query
        if t < optimized_ways_by_car[x - 1][y - 1]:
            optimized_ways_by_car[x - 1][y - 1] = t
            optimized_ways_by_car[y - 1][x - 1] = t
    elif query[0] == 2:
        _, x = query
        airports.add(x)
    else:
        for i in range(n):
            for j in range(n):
                transport_time = min(
                    optimized_ways_by_car[i][j],
                    t if i + 1 in airports and j + 1 in airports else float("inf"),
                )
                ans += transport_time if transport_time != float("inf") else 0
        print(ans)
