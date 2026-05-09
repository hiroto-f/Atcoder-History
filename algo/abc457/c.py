import sys

input = sys.stdin.readline

N, K = map(int, input().split())
A = []
L = []

for _ in range(N):
    row = list(map(int, input().split()))
    L.append(row[0])
    A.append(row[1:])

C = list(map(int, input().split()))

before = 0

for i in range(N):
    block_len = L[i] * C[i]
    if before + block_len >= K:
        index = (K - before - 1) % L[i]
        print(A[i][index])
        break
    before += block_len
