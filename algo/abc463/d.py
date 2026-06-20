def can_choose(cloths, k, distance):
    count = 0
    last_right = -(10**30)

    for left, right in cloths:
        ## この場合は、次の布として選べる
        if last_right + distance <= left:
            count += 1
            last_right = right

            if count == k:
                return True
    return False


def main():
    n, k = map(int, input().split())
    cloths = []

    for _ in range(n):
        left, right = map(int, input().split())
        cloths.append((left, right))

    # 右端を用いてソートする
    cloths.sort(key=lambda x: x[1])

    # スコア1で無理なら無理
    if not can_choose(cloths, k, 1):
        print(-1)
        return

    ## 二分探索
    ok = 1
    ng = 10**9 + 1

    while ng - ok > 1:
        mid = (ok + ng) // 2

        if can_choose(cloths, k, mid):
            ok = mid
        else:
            ng = mid

    print(ok)


if __name__ == "__main__":
    main()
