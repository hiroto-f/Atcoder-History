import math
N, M = map(int, input().split())

max_member = math.ceil(N / 2)

if M <= max_member:
    print("Yes")
else:    print("No")