x, y = map(int, input().split())

DIFF = 1e-9

if 16 / 9 - DIFF < x / y < 16 / 9 + DIFF:
    print("Yes")
else:
    print("No")
