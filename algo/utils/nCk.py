def comb(n, k):
    nCk = 1
    MOD = 998244353

    for i in range(n - k + 1, n + 1):
        nCk *= i
        nCk %= MOD

    for i in range(1, k + 1):
        nCk *= pow(i, MOD - 2, MOD)
        nCk %= MOD
    return nCk
