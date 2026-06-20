n, x = input().split()
n = int(n)
ans = False

match x:
    case "A":
        x = 0
    case "B":
        x = 1
    case "C":
        x = 2
    case "D":
        x = 3
    case "E":
        x = 4
    case _:
        x = 5

for i in range(n):
    s = input()
    if s[x] == "o":
        ans = True
        break

print("Yes" if ans else "No")
