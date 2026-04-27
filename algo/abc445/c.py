N = int(input())
A = [x - 1 for x in map(int, input().split())]

# i <= A_i なので、移動先は必ず右か同じマス。
# したがって各マスは最終的に自己ループのマスへ到達する。
final = [-1] * N

for s in range(N):
    if final[s] != -1:
        continue

    path = []
    v = s
    while final[v] == -1:
        path.append(v)
        if A[v] == v:  # 自己ループ
            final[v] = v
            break
        v = A[v]

    dst = final[v]
    for u in path:
        final[u] = dst

print(*[x + 1 for x in final])
