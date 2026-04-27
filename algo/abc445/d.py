H, W ,N = map(int, input().split())

dicts = {}

for i in range(N):
    h, w = map(int, input().split())
    dicts[i] = [h,w]

dicts_height = dict(sorted(dicts.items(), key=lambda x: x[1][0], reverse=True))
dicts_width = dict(sorted(dicts.items(), key=lambda x: x[1][1], reverse=True))

def pick_proper_block(current_H, current_W, dicts_height, dicts_width) -> list:
    biggest_height_block = next(iter(dicts_height.items()))
    biggest_width_block = next(iter(dicts_width.items()))
    # print("current_H, current_W, biggest_height_block, biggest_width_block",current_H, current_W, biggest_height_block, biggest_width_block)
    if biggest_height_block[1][0] == current_H:
        return [biggest_height_block[0], "height"]
    elif biggest_width_block[1][1] == current_W:
        return [biggest_width_block[0], "width"]
    else:        
        return [-1, ""]

current_H = H
current_W = W

current_start_point = [1,1]

ans = [[-1] for _ in range(N)]

for i in range(N):
    [block_index, direction] = pick_proper_block(current_H, current_W, dicts_height, dicts_width)
    if block_index == -1:
        ## これは起こらない想定
        print("No")
        exit()
    else:
        ans[block_index] = current_start_point
        if direction == "width":
            current_start_point = [current_start_point[0] + dicts[block_index][0], current_start_point[1]]
            current_H = current_H - dicts[block_index][0]
        elif direction == "height":
            current_start_point = [current_start_point[0], dicts[block_index][1] + current_start_point[1]]
            current_W = current_W - dicts[block_index][1]
        # print("current_start_point", current_start_point)
        del dicts_height[block_index]
        del dicts_width[block_index]
        del dicts[block_index]

for a in ans:
    print(*a)


# ans
# 2 5
# 1 3
# 2 3
# 4 5
# 2 4
# 1 1