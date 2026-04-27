import sys
input = sys.stdin.readline

N = int(input())

A = []
B = []
for _ in range(N):
    a, b = map(int, input().split())
    A.append(a)
    B.append(b)

M = int(input())
S = [input().strip() for _ in range(M)]

# present[len][pos]
present = [[set() for _ in range(11)] for _ in range(11)]

for s in S:
    l = len(s)
    for i, ch in enumerate(s):
        present[l][i+1].add(ch)

for t in S:
    if len(t) != N:
        print("No")
        continue

    ok = True
    for i in range(N):
        if t[i] not in present[A[i]][B[i]]:
            ok = False
            break

    print("Yes" if ok else "No")