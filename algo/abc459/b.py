N = int(input())
S = input().split()

ans = ""
for s in S:
    if s[0] in ["a", "b", "c"]:
        ans += "2"
    elif s[0] in ["d", "e", "f"]:
        ans += "3"
    elif s[0] in ["g", "h", "i"]:
        ans += "4"
    elif s[0] in ["j", "k", "l"]:
        ans += "5"
    elif s[0] in ["m", "n", "o"]:
        ans += "6"
    elif s[0] in ["p", "q", "r", "s"]:
        ans += "7"
    elif s[0] in ["t", "u", "v"]:
        ans += "8"
    elif s[0] in ["w", "x", "y", "z"]:
        ans += "9"

print(ans)
