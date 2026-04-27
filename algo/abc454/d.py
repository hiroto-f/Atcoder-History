def normalize(s):
    stack = []

    for ch in s:
        stack.append(ch)

        while len(stack) >= 4 and stack[-4:] == ["(", "x", "x", ")"]:
            ## 全ての(xx)をxxに置換する
            stack.pop()
            stack.pop()
            stack.pop()
            stack.pop()
            stack.append("x")
            stack.append("x")

    return "".join(stack)


T = int(input())

for _ in range(T):
    A = input().strip()
    B = input().strip()

    if normalize(A) == normalize(B):
        print("Yes")
    else:
        print("No")
