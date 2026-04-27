N, M = map(int, input().split())
F = list(map(int, input().split()))

clothes = [0] * (M)

for f in F:
    clothes[f - 1] += 1

if max(clothes) > 1:
    print("No")
else:
    print("Yes")

if min(clothes) > 0:
    print("Yes")
else:    print("No")
