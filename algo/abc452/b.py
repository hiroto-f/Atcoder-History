H, W = map(int, input().split())

for i in range(H):
    if i == 0 or i == H-1:
        print("#" * W)
    else:
        print("#" + "." * (W-2) + "#")