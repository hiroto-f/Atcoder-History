## このリストはなんでも良い
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
