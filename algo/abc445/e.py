import math

def lcm_mod(numbers, mod):
    result = 1
    for x in numbers:
        g = math.gcd(result, x)
        result = (result // g) * x
        result %= mod
    return result

ans = []

T = int(input())

for _ in range(T):
    N = int(input())
    A = list(map(int, input().split()))
    ans_items = []
    for n in range(N):
        ans_items.append(lcm_mod(A[:n] + A[n+1:], 998244353))
    ans.append(ans_items)

for a in ans:
    print(*a)
