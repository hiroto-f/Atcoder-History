N, Q = map(int, input().split())

## 各カードは自分の上にあるカードと下にあるカードを見れる
below = [0] * (N + 1)
above = [0] * (N + 1)

for _ in range(Q):
    c, p = map(int, input().split())
    b = below[c]
    if b != 0:
        above[b] = 0
    below[c] = p
    above[p] = c

ans = [0] * (N + 1)

for i in range(1, N + 1):
    if below[i] != 0:
        ## すでに下にカードがある場合は、山iにはカードがない
        continue

    count = 0
    cur = i
    while cur != 0:
        count += 1
        cur = above[cur]
    ans[i] = count

print(*ans[1:])
