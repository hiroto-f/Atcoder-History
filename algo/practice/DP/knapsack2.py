N, W = map(int, input().split())
V = 0

weights = []
values = []

for i in range(N):
    w, v = map(int, input().split())
    weights.append(w)
    values.append(v)
    V += v

dp = [[0] * (N+1)] + [[float("inf")] * (N+1) for _ in range(V)]

for v in range(1, V+1):
    ## v = 1,2, ..., W
    for n in range(1,N+1):
        if values[n-1] <= v:
            dp[v][n] = min(dp[v][n-1], dp[v-values[n-1]][n-1] + weights[n-1])
        else:
            dp[v][n] = dp[v][n-1]

for v in range(V, 0, -1):
    # print("v:", v, "dp[v][N]:", dp[v][N])
    if dp[v][N] <= W:
        V = v
        break

print(V)
