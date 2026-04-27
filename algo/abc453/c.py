N = int(input())
L = list(map(int, input().split()))

## 方針
## 2**N通りの選び方がある
## それぞれの選び方を二進数で表し、01を符号と解釈して全パターンを試す

ans = 0

for binary_i in range(1 << N):
    current = 1 ## 整数にしたいので2倍した
    count = 0

    for j in range(N):
        if (binary_i >> j) & 1: ## j番目のビットが1かどうか
            next_point = current + 2 * L[j]
        else:
            next_point = current - 2 * L[j]
        if (current < 0 and next_point > 0) or (current > 0 and next_point < 0):
            count += 1
        current = next_point

    ans = max(ans, count)

print(ans)