import sys


INF = 10**30


def main():
    input = sys.stdin.readline

    n, m = map(int, input().split())
    hub = n
    v = n + 1

    dist = [[INF] * v for _ in range(v)]
    for i in range(v):
        dist[i][i] = 0

    for _ in range(m):
        a, b, c = map(int, input().split())
        a -= 1
        b -= 1
        if c < dist[a][b]:
            dist[a][b] = c
            dist[b][a] = c

    k, airport_time = map(int, input().split())
    airports = list(map(int, input().split()))
    for d in airports:
        d -= 1
        dist[d][hub] = 0
        dist[hub][d] = airport_time

    ## Floyd-Warshall 法
    for mid in range(v):
        dist_mid = dist[mid]
        for i in range(v):
            via = dist[i][mid]
            if via == INF:
                continue
            dist_i = dist[i]
            base = via
            for j in range(v):
                nd = base + dist_mid[j]
                if nd < dist_i[j]:
                    dist_i[j] = nd

    total = 0
    for i in range(n):
        dist_i = dist[i]
        for j in range(n):
            if dist_i[j] != INF:
                total += dist_i[j]

    def add_directed_edge(a, b, cost, total):
        if cost >= dist[a][b]:
            return total

        for i in range(v):
            ia = dist[i][a]
            if ia == INF:
                continue

            dist_i = dist[i]
            base = ia + cost
            for j in range(v):
                bj = dist[b][j]
                if bj == INF:
                    continue

                nd = base + bj
                if nd < dist_i[j]:
                    old = dist_i[j]
                    dist_i[j] = nd
                    if i < n and j < n:
                        if old == INF:
                            total += nd
                        else:
                            total += nd - old

        return total

    q = int(input())
    ans = []

    for _ in range(q):
        query = list(map(int, input().split()))

        if query[0] == 1:
            _, x, y, t = query
            x -= 1
            y -= 1
            total = add_directed_edge(x, y, t, total)
            total = add_directed_edge(y, x, t, total)
        elif query[0] == 2:
            _, x = query
            x -= 1
            total = add_directed_edge(x, hub, 0, total)
            total = add_directed_edge(hub, x, airport_time, total)
        else:
            ans.append(str(total))

    print("\n".join(ans))


if __name__ == "__main__":
    main()
