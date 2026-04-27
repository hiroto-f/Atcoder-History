#!/usr/bin/env python3
import sys
import time
import math
import random

DEBUG = True  # 本番提出時は必ず False（stderr含め追加出力なしにするのが安全）

def read_ints(n):
    """Read exactly n integers from stdin (space/newline separated)."""
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

def build_cards(N, M, L, U):
    """二進層でカード A を構築し、(A, layers, s, layer_values) を返す。"""
    base_count = M
    remaining = max(0, N - base_count)
    max_layers = remaining // M
    R = U - L

    if R <= 0 or max_layers <= 0:
        layers = 0
        s = 0
    else:
        # s を小さくするため利用可能な最大段数を使う
        layers = max_layers
        denom = (1 << layers) - 1
        s = (R + denom - 1) // denom

    A = []
    # Base: L を M 枚
    for _ in range(M):
        A.append(L)

    # 調整層: k=0..layers-1, 額面 dv=(1<<k)*s を各 M 枚
    layer_values = []
    for k in range(layers):
        dv = (1 << k) * s
        layer_values.append(dv)
        for _ in range(M):
            A.append(dv)

    # 余りがあれば 1 で埋める（今回は N=500, M=50, layers=9 でちょうど埋まる）
    if len(A) < N:
        A.extend([1] * (N - len(A)))

    return A, layers, s, layer_values

def greedy_assign(A, M, L, B, layers, layer_values):
    """土台＋上位額面からの貪欲で初期解 X と S, E を作る。"""
    N = len(A)
    X = [0] * N
    # (a) Base L を一旦「山1..Mへ1枚ずつ」割当（必須ではないが良い初期化）
    for j in range(M):
        X[j] = j + 1

    # (b) delta_j = B_j - L を作り、上位層から貪欲
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
                X[idx] = 0  # 捨てる

    # S と E を計算
    S = [0] * M
    for i, pile in enumerate(X):
        if pile > 0:
            S[pile - 1] += A[i]
    # 誤差
    E = 0
    for j in range(M):
        E += abs(S[j] - B[j])
    return X, S, E

def anneal(A, M, B, X, S, E, time_limit_sec=1.6, seed=0xC0FFEE):
    """
    焼きなまし：単一移動（カード i を p->q, q∈{0..M}{p}）のみで E を改善。
    時間制約: time_limit_sec 秒（B 入力後からの持ち時間で調整して）。
    """
    random.seed(seed)

    N = len(A)
    # D_j = S_j - B_j を持っておくと ΔE の計算が楽
    D = [S[j] - B[j] for j in range(M)]

    # 温度スケジュール設定（E のオーダに合わせる）
    # 例：T0 ~ 1e10〜1e11, Tend ~ 1e2〜1e4 程度
    # E の大きさに応じて自動調整
    T0 = max(1.0, (E / max(1, M)))   # 1山あたりの誤差目安
    T0 = float(T0)
    Tend = 1.0

    start = time.time()
    it = 0
    best_E = E
    best_state = None  # 必要なら復元用（今回は割愛しても可）

    # 山の集合（0 は捨て山）
    ALL_PILES = list(range(0, M + 1))

    # SA ループ（時間管理）
    while True:
        t = time.time()
        elapsed = t - start
        if elapsed >= time_limit_sec:
            break

        # 進捗 0..1
        progress = elapsed / time_limit_sec
        # 指数冷却
        T = T0 * pow(Tend / T0, progress)
        if T < 1e-12:
            T = 1e-12

        # ランダムに 1 枚選び、別の行き先を提案
        i = random.randrange(N)
        v = A[i]
        p = X[i]           # 現在の山（0=捨て）
        # 別の山（含む捨て）を選択
        q = p
        # 小さなループで別 pile を引く
        for _ in range(3):
            q = random.choice(ALL_PILES)
            if q != p:
                break
        if q == p:
            continue

        # ΔE を高速評価
        # 影響するのは最大2山（p と q）。p=0 or q=0 の場合は1山だけ。
        old_part = 0
        new_part = 0

        if p != 0:
            Dp = D[p - 1]
            old_part += abs(Dp)
            Dp_new = Dp - v
            new_part += abs(Dp_new)
        if q != 0:
            Dq = D[q - 1]
            old_part += abs(Dq)
            Dq_new = Dq + v
            new_part += abs(Dq_new)

        dE = new_part - old_part

        # 受理判定
        if dE <= 0 or random.random() < math.exp(-dE / T):
            # 受理：状態更新
            if p != 0:
                D[p - 1] -= v
                S[p - 1] -= v
            if q != 0:
                D[q - 1] += v
                S[q - 1] += v
            X[i] = q
            E += dE

            if E < best_E:
                best_E = E
                # best_state = (X[:], S[:], D[:], E)  # 必要ならコピー
        it += 1

    if DEBUG:
        print(f"[debug] SA iters={it}  E_before={best_E + (E - best_E):.0f}  E_after={E:.0f}", file=sys.stderr)
    return X, S, E

def main():
    # ---- 1) 入力（1行で N M L U） ----
    N, M, L, U = map(int, sys.stdin.readline().split())

    # ---- 2) カード設計 A を構築し出力 ----
    A, layers, s, layer_values = build_cards(N, M, L, U)
    print(" ".join(map(str, A)))
    sys.stdout.flush()

    # ---- 3) 目標 B を読み取り ----
    B = read_ints(M)

    # ---- 4) 初期割当（貪欲） ----
    X, S, E = greedy_assign(A, M, L, B, layers, layer_values)

    # ---- 5) 焼きなましで改善（時間制御） ----
    # 競技環境 2 秒制限想定：A 出力〜B 入力〜最終出力で余裕を見て 1.6 秒などに
    # 実際は judge/PC に応じて調整してください。
    X, S, E = anneal(A, M, B, X, S, E, time_limit_sec=1.6, seed=123456)

    # ---- 6) 割当 X を 1 行出力 ----
    print(" ".join(map(str, X)))
    sys.stdout.flush()

if __name__ == "__main__":
    main()
