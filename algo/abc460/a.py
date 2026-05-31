N, M = map(int, input().split())

count = 0
while M > 0:
    count += 1
    x = N % M
    M = x

print(count)
