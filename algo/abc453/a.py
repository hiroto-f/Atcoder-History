N = int(input())
S = str(input())

ans = ""
not_o = False

for s in S:
    if not_o:
        ans += s
    elif s == "o":
        continue
    elif s != "o":
        ans += s
        not_o = True

print(ans)