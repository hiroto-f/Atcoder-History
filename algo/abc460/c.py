N, M = map(int, input().split())
A = list(map(int, input().split()))
B = list(map(int, input().split()))

A.sort()
B.sort()

ans = 0
j = 0

for a in A:
    if j < M and B[j] <= 2 * a:
        ans += 1
        j += 1

print(ans)
