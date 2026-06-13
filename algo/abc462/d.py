n, d = map(int, input().split())

num_by_time = [0] * (10**6 + 2)

for _ in range(n):
    s, t = map(int, input().split())
    if s + d <= t:
        num_by_time[s] += 1
        num_by_time[t - d + 1] -= 1

ans = 0
n_num = 0
for diff in num_by_time:
    n_num += diff
    ans += n_num * (n_num - 1) // 2

print(ans)
