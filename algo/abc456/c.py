MOD = 998244353

S = input().strip()

ans = 0
current = 0
prev = ""

for ch in S:
    if ch == prev:
        current = 1
    else:
        current += 1

    ans = (ans + current) % MOD
    prev = ch

print(ans)
