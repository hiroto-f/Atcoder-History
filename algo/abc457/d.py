N, K = map(int, input().split())
A = list(map(int, input().split()))

## 判別関数 O(N)
def can(x):
    count = 0
    for i, a in enumerate(A, start=1):
        if a < x:
            count += (x - a + i - 1) // i
            if count > K:
                return False
    return True


ok = min(A)
ng = ok + K * N + 1 ## 最大値

## 二分探索 log(KN)
while ng - ok > 1:
    mid = (ok + ng) // 2
    if can(mid):
        ok = mid
    else:
        ng = mid

print(ok)
