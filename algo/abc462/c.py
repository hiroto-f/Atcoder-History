N = int(input())
y_by_x = [0] * (N + 1)

for _ in range(N):
    x, y = map(int, input().split())
    y_by_x[x] = y

ans = 0
min_y = N + 1

for x in range(1, N + 1):
    y = y_by_x[x]

    if y < min_y:
        ans += 1
        min_y = y

print(ans)
