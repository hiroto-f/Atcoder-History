N, M = input().split()
N = int(N)
M = int(M)

number_per_dep = [0] * M
number_per_dep_next = [0] * M

for i in range(N):
    a, b = input().split()
    a = int(a)
    b = int(b)
    number_per_dep[a-1] += 1
    number_per_dep_next[b-1] += 1

for i in range(M):
    print(number_per_dep_next[i]-number_per_dep[i])
