def build_path(n, a, b):
    if n % 2 == 1 or (a + b) % 2 == 0:
        ## nが奇数、または、(a, b)が同じ色のマスにいる時は無理
        return None


    special_left = b if b % 2 == 1 else b - 1 # 特別な列の左側の列番号
    moves = []
    row, col = 1, 1

    def move(ch):
        nonlocal row, col
        moves.append(ch)
        if ch == "L":
            col -= 1
        elif ch == "R":
            col += 1
        elif ch == "U":
            row -= 1
        else:
            row += 1

    for left_col in range(1, special_left, 2):
        for _ in range(n - 1):
            move("D")
        move("R")
        for _ in range(n - 1):
            move("U")
        move("R")

    while row < n:
        other_col = special_left + 1 if col == special_left else special_left
        if (row, other_col) != (a, b) and (row + 1, other_col) != (a, b):
            move("R" if col == special_left else "L")
        move("D")

    if col != special_left + 1:
        move("R")

    for left_col in range(special_left + 2, n, 2):
        move("R")
        for _ in range(n - 1):
            move("U")
        move("R")
        for _ in range(n - 1):
            move("D")

    return "".join(moves)


t = int(input())
out = []

for _ in range(t):
    n, a, b = map(int, input().split())
    path = build_path(n, a, b)
    if path is None:
        out.append("No")
    else:
        out.append("Yes")
        out.append(path)

print("\n".join(out))

