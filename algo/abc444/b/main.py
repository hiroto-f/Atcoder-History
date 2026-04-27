N, K = map(int, input().split())

ans = 0
for x in range(1, N + 1):
    if sum(map(int, str(x))) == K:
        ans += 1

print(ans)
