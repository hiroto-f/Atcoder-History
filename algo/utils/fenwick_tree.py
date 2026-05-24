# Fenwick Tree / BIT
# 0-indexed の配列 a を扱う。
#
# 使い方:
#   any_list = [0] * (N + 1)  # N は管理したい要素数
#   add(i, x)                 # a[i] に x を足す
#   sum_(r)                   # a[0] + ... + a[r-1] を返す
#   sum_(r) - sum_(l)         # 区間 [l, r) の和
#
# 注意:
#   add の i は 0-indexed。
#   sum_ の引数 r は「先頭から r 個分」の意味なので、sum_(0) は 0。
#   any_list の長さは N + 1 以上にする。
any_list = [0] * 100001


def add(i, x):
    i += 1
    while i < len(any_list):
        any_list[i] += x
        i += i & -i


def sum_(i):
    res = 0
    while i > 0:
        res += any_list[i]
        i -= i & -i
    return res
