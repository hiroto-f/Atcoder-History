N = int(input())
S = []
m = 0

for _ in range(N):
    S.append(str(input()))
    if len(S[-1]) > m:
        m = len(S[-1])

T = []
for s in S:
    if len(s) == m:
        T.append(s)
    else:
        k = (m - len(s)) / 2
        T.append("." * int(k) + s + "." * int(k))

for t in T:
    print(t)