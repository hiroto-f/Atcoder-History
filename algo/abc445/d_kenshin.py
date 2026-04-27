import sys

input = sys.stdin.readline
sys.setrecursionlimit(10**7)


def main():
    h, w, n = map(int, input().split())
    dict_h = {}
    dict_w = {}
    for i in range(n):
        x, y = map(int, input().split())
        dict_h[i] = (x, y)
        dict_w[i] = (y, x)
    # 高さ基準でsort
    dict_h = dict(sorted(dict_h.items(), key=lambda item: item[1][0]))
    # 横基準でsort
    dict_w = dict(sorted(dict_w.items(), key=lambda item: item[1][0]))

    # 高さh と 横wを見つけて次のnew_hとnew_wを出力する。座標(current_h,current_w)から次の座標を(next_x,next_y)を出力。
    def pick_proper_block(dict_h, dict_w, h, w, current_h, current_w):
        # 一番右側のkeyを見つける
        last_key_h = next(reversed(dict_h))
        last_key_w = next(reversed(dict_w))
        target_index = -1
        if dict_h[last_key_h][0] == h:
            item_h = dict_h.popitem()
            target_index = item_h[0]
            dict_w.pop(item_h[0])
            new_h = h
            new_w = w - item_h[1][1]
            next_y = current_w + item_h[1][1]
            next_x = current_h
        elif dict_w[last_key_w][0] == w:
            item_w = dict_w.popitem()
            target_index = item_w[0]
            dict_h.pop(item_w[0])
            new_h = h - item_w[1][1]
            new_w = w
            next_y = current_w
            next_x = current_h + item_w[1][1]
        return new_h, new_w, next_x, next_y, target_index

    x = 1
    y = 1
    h_list = h
    w_list = w

    ans_list = [(-1,1) for _ in range(n)]

    print(x, y)
    for i in range(n-1):
        new_h, new_w, next_x, next_y, target_index = pick_proper_block(
            dict_h, dict_w, h_list, w_list, x, y
        )
        ans_list[target_index] = (x, y)
        ans_list[target_index] = (x, y)
        x = next_x
        y = next_y
        h_list = new_h
        w_list = new_w
        print(next_x, next_y)


if __name__ == "__main__":
    main()
