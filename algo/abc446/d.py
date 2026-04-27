N = int(input())
A = list(map(int, input().split()))

B_last = [] ## 最後の値
B_number = [] ## 連続している数の個数

for a in A:
    if a in B_last:
        continue
    else:
        idx = -1
        for i, x in enumerate(B_last):
            if x == a - 1:
                idx = i
                B_last[idx] = a
                B_number[idx] += 1
        if idx == -1:
            B_last.append(a)
            B_number.append(1)

print(max(B_number))
