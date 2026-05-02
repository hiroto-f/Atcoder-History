MOD = 998244353

S = input().strip()

## xで終わっている有効な部分列の数をdp[x]とする
dp = {"a": 0, "b": 0, "c": 0}

total = 0

for ch in S:
    add = (1 + total - dp[ch]) % MOD
    dp[ch] = dp[ch] + add
    total = (total + add) % MOD

print(total)
