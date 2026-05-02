from collections import deque
import sys


def build_graph(n, m, input):
    graph = [[] for _ in range(n)]
    for _ in range(m):
        u, v = map(int, input().split())
        u -= 1
        v -= 1
        graph[u].append(v)
        graph[v].append(u)
    return graph


def solve(input):
    N, M = map(int, input().split())
    graph = build_graph(N, M, input)
    W = int(input())
    S = [input().strip() for _ in range(N)]

    total = N * W
    ## state = v * W + d として、都市vのd曜日にの昼間が休日ならTrue
    alive = [False] * total
    ## stateから出る辺の数
    outdeg = [0] * total
    q = deque()

    ## N個の都市に対して実験する
    for v in range(N):
        sv = S[v]
        ## 全ての曜日で昼間が休日か
        for d in range(W):
            ## いきなり平日ならスキップ
            if sv[d] == "x":
                continue

            state = v * W + d
            alive[state] = True

            nd = (d + 1) % W
            cnt = 1 if sv[nd] == "o" else 0
            for to in graph[v]:
                if S[to][nd] == "o":
                    cnt += 1

            outdeg[state] = cnt
            if cnt == 0:
                q.append(state)

    while q:
        ## 死んでいる状態から出発し、その状態に来られる状態を全て死なせる。
        state = q.popleft()
        if not alive[state]:
            continue

        alive[state] = False
        v, d = divmod(state, W)
        pd = (d - 1) % W

        # 前日の夜に v へ来られる状態を更新する。
        prev_state = v * W + pd
        if alive[prev_state]:
            outdeg[prev_state] -= 1
            if outdeg[prev_state] == 0:
                q.append(prev_state)

        for frm in graph[v]:
            prev_state = frm * W + pd
            if alive[prev_state]:
                outdeg[prev_state] -= 1
                if outdeg[prev_state] == 0:
                    q.append(prev_state)

    for v in range(N):
        ## 初日の状態が生きているならYesを返す
        if alive[v * W]:
            return "Yes"

    return "No"


def main():
    input = sys.stdin.readline
    T = int(input())
    ans = [solve(input) for _ in range(T)]
    print("\n".join(ans))


if __name__ == "__main__":
    main()
