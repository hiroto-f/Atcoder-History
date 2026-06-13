t = int(input())
ans_list = []

for _ in range(t):
    a, b, x, y = map(int, input().split())

    def even_cost(x, y):
        x, y = abs(x), abs(y)
        diagonal = min(x, y)
        straight = abs(x - y) // 2
        return diagonal * (2 * min(a, b)) + straight * min(a + b, 4 * min(a, b))

    if (abs(x) + abs(y)) % 2 == 0:
        ans = even_cost(x, y)
    else:
        ans = min(
            a + even_cost(x - 1, y),
            a + even_cost(x + 1, y),
            b + even_cost(x, y - 1),
            b + even_cost(x, y + 1),
        )

    ans_list.append(ans)

print(*ans_list, sep="\n")
