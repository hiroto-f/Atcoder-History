N = int(input())

K = []
A = []

for _ in range(N):
    values = list(map(int, input().split()))
    K.append(values[0])
    A.append(values[1:])

received_num = [[] for _ in range(N)]

for i in range(N):
    ## i番目の人が送るプレゼント
    for to in A[i]:
        received_num[to - 1].append(i + 1)

for i in range(N):
    print(len(received_num[i]), *received_num[i])
