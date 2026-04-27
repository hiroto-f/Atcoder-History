import sys
sys.setrecursionlimit(10**7)

MOD = 998244353

class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n
        self.comp = n  # 連結成分数

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def unite(self, a, b):
        a = self.find(a)
        b = self.find(b)
        if a == b:
            return False
        if self.size[a] < self.size[b]:
            a, b = b, a
        self.parent[b] = a
        self.size[a] += self.size[b]
        self.comp -= 1
        return True


def main():
    N, M = map(int, input().split())

    edges = []
    for i in range(1, M + 1):
        u, v = map(int, input().split())
        edges.append((u - 1, v - 1, i))  

    pow2 = [1] * (M + 1)
    for i in range(1, M + 1):
        pow2[i] = (pow2[i - 1] * 2) % MOD

    uf = UnionFind(N)

    # 重い辺から繋いでいく
    for u, v, i in reversed(edges): 
        if uf.comp <= 2:
            break
        uf.unite(u, v)
        # print(f'今結合したのは、{u, v, i}')

    ans = 0
    for u, v, i in edges:
        if uf.find(u) != uf.find(v):
            ans += pow2[i]
            ## 計算量対策
            if ans >= MOD:
                ans -= MOD

    print(ans % MOD)

if __name__ == "__main__":
    main()