N = int(input())
A = []

for _ in range(N):
    row = list(map(int, input().split()))
    A.append(row[1:])

X, Y = map(int, input().split())
print(A[X - 1][Y - 1])
