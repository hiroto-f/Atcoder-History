#!/usr/bin/env python3
import sys
from math import log10

DEBUG_SCORE = True  


def read_ints(n):
    """Read exactly n integers from stdin (space or newline separated)."""
    vals = []
    while len(vals) < n:
        line = sys.stdin.readline()
        if not line:
            break
        parts = line.strip().split()
        for p in parts:
            if p:
                vals.append(int(p))
                if len(vals) >= n:
                    break
    return vals

def main():
    # --- 1) read N, M, L, U ---
    # N, M, L, U = map(int, sys.stdin.readline().split())
    N, M, L, U = 500, 50, 998000000000000, 1002000000000000

    # --- 2) decide layers and step ---
    base_count = M
    remaining = max(0, N - base_count)
    max_layers = remaining // M  # 調整層に回せる最大段数（各層 M 枚必要）
    R = U - L

    if R <= 0 or max_layers <= 0:
        layers = 0
        s = 0
    else:
        layers = max_layers
        denom = (1 << layers) - 1
        s = (R + denom - 1) // denom # ceil(R / denom)　調整幅の単位

    # --- 3) build A ---
    A = []
    for _ in range(M):
        A.append(L)

    layer_values = []
    for k in range(layers):
        dv = (1 << k) * s
        layer_values.append(dv)
        for _ in range(M):
            A.append(dv)

    if len(A) < N:
        A.extend([1] * (N - len(A)))

    # --- 4) output A (one line) ---
    print(" ".join(map(str, A)))
    sys.stdout.flush()

    # --- 5) read B ---
    B = read_ints(M)

    # --- 6) build assignment X ---
    X = [0] * N
    for j in range(M):
        # 最初の M 枚は必ず取る
        X[j] = j + 1

    delta = [bj - L for bj in B]
    for k in range(layers - 1, -1, -1):
        dv = layer_values[k]
        base_idx = M + k * M
        for j in range(M):
            idx = base_idx + j
            if delta[j] >= dv:
                X[idx] = j + 1
                delta[j] -= dv
            else:
                X[idx] = 0


    # --- 7) output X (one line) ---
    print(" ".join(map(str, X)))
    sys.stdout.flush()

    # --- 8) スコア計算（stderr に出力） ---
    if DEBUG_SCORE:
        # 各山の合計 S_j を計算
        S = [0] * M
        for i in range(N):
            pile = X[i]
            if pile > 0:
                S[pile - 1] += A[i]
        # 誤差 E
        E = 0
        for j in range(M):
            E += abs(S[j] - B[j])
        # スコア
        # score = round((20 - log10(1 + E)) * 5 * 10**7)
        # log10(1+E) は E=0 のときも OK
        score = round((20 - log10(1 + E)) * 5 * (10 ** 7))
        print(f"[debug] E={E}  score={score}", file=sys.stderr)

if __name__ == "__main__":
    main()
