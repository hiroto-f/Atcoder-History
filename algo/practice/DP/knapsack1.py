N, W = map(int, input().split())

weights = []
values = []

for i in range(N):
    w, v = map(int, input().split())
    weights.append(w)
    values.append(v)

dp = [[0] * (N+1) for _ in range(W+1)]

dp[0][0] = 0

for w in range(1, W+1):
    ## w = 1,2, ..., W
    for n in range(1,N+1):

        if weights[n-1] <= w:
            if w-weights[n-1] >= 0:
                dp[w][n] = max(dp[w][n-1], dp[w-weights[n-1]][n-1] + values[n-1])
            else:
                dp[w][n] = dp[w][n-1]
        else:
            dp[w][n] = dp[w][n-1]

print(dp[W][N])