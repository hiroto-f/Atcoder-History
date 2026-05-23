N, Q = map(int, input().split())

n_list = [0] * N
total_list = [0] * (Q + 2)


def add(i, x):
    i += 1
    while i < len(total_list):
        total_list[i] += x
        i += i & -i


def sum_(i):
    res = 0
    while i > 0:
        res += total_list[i]
        i -= i & -i
    return res


add(0, N)

# 何回全体から-1したか
count = 0

for _ in range(Q):
    process, index = input().split()
    index = int(index)

    if process == "1":
        index -= 1
        add(n_list[index], -1)
        n_list[index] += 1
        add(n_list[index], 1)

        if sum_(count + 1) == 0:
            count += 1
    else:
        if count + index >= len(total_list):
            print(0)
        else:
            print(N - sum_(count + index))
