MOD = 998244353


def init_comb(max_n):
    fact = [1] * (max_n + 1)
    inv_fact = [1] * (max_n + 1)

    for i in range(1, max_n + 1):
        fact[i] = fact[i - 1] * i % MOD

    inv_fact[max_n] = pow(fact[max_n], MOD - 2, MOD)
    for i in range(max_n, 0, -1):
        inv_fact[i - 1] = inv_fact[i] * i % MOD

    return fact, inv_fact


fact = []
inv_fact = []


def comb(n, k):
    if k < 0 or n < k:
        return 0
    return fact[n] * inv_fact[k] % MOD * inv_fact[n - k] % MOD


x1, x2, x3 = map(int, input().split())

fact, inv_fact = init_comb(x1 + x2 + x3 + 5)

between_2 = x2 + 1
n = between_2

ans = 0
for r in range(1, min(x1, n) + 1):
    ans += comb(n, r) * comb(x1 - 1, r - 1) * comb(x3 + n - r - 1, x3)

    ans %= MOD

print(ans % MOD)
