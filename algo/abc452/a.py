target_five = [(1,7), (3,3), (5,5), (7,7), (9,9)]

M, D = map(int, input().split())
if (M, D) in target_five:
    print("Yes")
else:    print("No")