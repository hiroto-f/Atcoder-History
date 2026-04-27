N, M = map(int, input().split())

L = []
X = []

for i in range(N):
    l = int(input())
    L.append(l)
    x = list(map(int, input().split()))
    X.append(x)

N_drink = [0 for _ in range(N)]
M_taken = [False for _ in range(M)]

for i in range(N):
    for x in X[i]:
        if not M_taken[x - 1]:
            M_taken[x - 1] = True
            N_drink[i] = x
            break

for i in range(N):
    print(N_drink[i])

