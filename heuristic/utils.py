class Random:
    """軽量な疑似乱数生成器。

    使い方:
        rng = Random(seed)
        rng.next()        # 64bit整数風の値を返す
        rng.randrange(n)  # 0 <= x < n の整数を返す
        rng.random()      # 0.0 <= x < 1.0 の浮動小数を返す
    """

    def __init__(self, seed):
        self.x = seed & ((1 << 64) - 1)
        if self.x == 0:
            self.x = 88172645463325252

    def next(self):
        x = self.x
        x ^= (x << 7) & ((1 << 64) - 1)
        x ^= x >> 9
        self.x = x
        return x

    def randrange(self, n):
        return self.next() % n

    def random(self):
        return (self.next() >> 11) * (1.0 / (1 << 53))