from collections import defaultdict

N = int(input())
A = list(map(int, input().split()))

## defaultdict(int)は、末尾がintの部分列の長さの最大値を保持する
d = defaultdict(int)

for a in A:
    d[a] = max(d[a], d[a - 1] + 1)

print(max(d.values()))

