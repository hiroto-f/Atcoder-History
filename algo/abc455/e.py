from collections import defaultdict


N = int(input())
S = input()

total = N * (N + 1) // 2

count_a = 0
count_b = 0
count_c = 0

seen_ab = defaultdict(int)
seen_ac = defaultdict(int)
seen_bc = defaultdict(int)
seen_all = defaultdict(int)

seen_ab[0] = 1
seen_ac[0] = 1
seen_bc[0] = 1
seen_all[(0, 0)] = 1

f_ab = 0
f_ac = 0
f_bc = 0
f_all = 0

for ch in S:
    if ch == "A":
        count_a += 1
    elif ch == "B":
        count_b += 1
    else:
        count_c += 1

    diff_ab = count_a - count_b
    diff_ac = count_a - count_c
    diff_bc = count_b - count_c

    f_ab += seen_ab[diff_ab]
    f_ac += seen_ac[diff_ac]
    f_bc += seen_bc[diff_bc]
    f_all += seen_all[(diff_ab, diff_ac)]

    seen_ab[diff_ab] += 1
    seen_ac[diff_ac] += 1
    seen_bc[diff_bc] += 1
    seen_all[(diff_ab, diff_ac)] += 1

answer = total - f_ab - f_ac - f_bc + 2 * f_all
print(answer)
