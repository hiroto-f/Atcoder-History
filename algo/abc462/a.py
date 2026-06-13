s = input()

ans = ""

for string in s:
    if string.isdigit():
        ans += string

print(ans)
