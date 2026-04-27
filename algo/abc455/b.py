def check_point_symmetry(grid, left, right, top, bottom):
    ## 点対象な長方形になっているかを確認する
    for i in range(top, bottom + 1):
        for j in range(left, right + 1):
            if grid[i][j] != grid[bottom - (i - top)][right - (j - left)]:
                return False
    return True


H, W = map(int, input().split())
grid = []

for i in range(H):
    s = str(input())
    grid.append(s)

ans = 0
for h1 in range(H):
    for h2 in range(h1, H):
        for w1 in range(W):
            for w2 in range(w1, W):
                if check_point_symmetry(grid, w1, w2, h1, h2):
                    ans += 1

print(ans)


