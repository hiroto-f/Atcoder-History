import sys
import string

input = sys.stdin.readline

S = input().strip()
T = input().strip()

n = len(S)
m = len(T)

pos = {ch: [] for ch in string.ascii_lowercase}
for i, ch in enumerate(T):
    pos[ch].append(i)

dp = [-1] * (m + 1)

ans = 0
for r, ch in enumerate(S):
    for j in reversed(pos[ch]):
        if j == 0:
            dp[1] = max(dp[1], r)
        elif dp[j] != -1:
            dp[j + 1] = max(dp[j + 1], dp[j])

    if dp[m] == -1:
        ans += r + 1
    else:
        ans += r - dp[m]

print(ans)
