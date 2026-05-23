MOD = 998244353


def comb(n, k):
    nCk = 1

    for i in range(n - k + 1, n + 1):
        nCk *= i
        nCk %= MOD

    for i in range(1, k + 1):
        nCk *= pow(i, MOD - 2, MOD)
        nCk %= MOD
    return nCk


N = int(input())
P = list(map(int, input().split()))
C = list(map(int, input().split()))
D = list(map(int, input().split()))

children = [[] for _ in range(N)]
for i, p in enumerate(P, 1):
    children[p - 1].append(i)


## 計算順序の作成
order = [0]
for v in order:
    order.extend(children[v])

rest = [0] * N
ans = 1


## 頂点Nから数える
for v in reversed(order):
    total = C[v]
    for child in children[v]:
        total += rest[child]

    ans = ans * comb(total, D[v]) % MOD
    rest[v] = total - D[v]

print(ans)
