N = int(input())
A = list(map(int, input().split()))
counts = {}
for value in A:
    counts[value] = counts.get(value, 0) + 1

mn = min(A)
mx = max(A)

candidates = {mx, mn + mx}
ans = []
for length in candidates:
    ok = True
    for value, cnt in counts.items():
        if value > length:
            ok = False
            break
        if value == length:
            continue

        pair = length - value
        if counts.get(pair, 0) != cnt:
            ok = False
            break

        if pair == value and cnt % 2 == 1:
            ok = False
            break

    if ok:
        ans.append(length)

ans.sort()

print(*ans)
