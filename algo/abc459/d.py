from collections import Counter

case_count = int(input())
ans = []

for _ in range(case_count):
    S = input().strip()
    N = len(S)
    cnt = Counter(S)

    ## 一番多い文字を他の文字で挟む
    if max(cnt.values()) > (N + 1) // 2:
        ans.append("No")
        continue

    chars = []
    for c, num in sorted(cnt.items(), key=lambda x: x[1], reverse=True):
        chars.extend([c] * num)

    result = [""] * N
    index = 0
    ## まず偶数indexに多い文字から配置する
    for c in chars:
        result[index] = c
        index += 2
        ## ここで奇数indexに移る
        if index >= N:
            index = 1

    ans.append("Yes")
    ans.append("".join(result))

print("\n".join(ans))
