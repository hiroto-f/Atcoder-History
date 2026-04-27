import sys
import time
import random
from dataclasses import dataclass
from copy import deepcopy

R = 10


@dataclass
class Move:
    type: int
    i: int
    j: int
    k: int


@dataclass
class Cand:
    move: Move
    score: int


class Solver:
    def __init__(self, init_dep, policy=0):
        self.init_dep = deepcopy(init_dep)
        self.policy = policy
        self.rng = random.Random(1234567 + policy * 1009)

        self.dep = []
        self.sid = []
        self.fixed_len = []
        self.turns = []

    def reset(self):
        self.dep = deepcopy(self.init_dep)
        self.sid = [[] for _ in range(R)]
        self.fixed_len = [0] * R
        self.turns = []

    def apply_move(self, m: Move):
        if m.type == 0:
            # 出発線 i の末尾 k 両 -> 待避線 j の先頭
            block = self.dep[m.i][-m.k:]
            del self.dep[m.i][-m.k:]
            self.sid[m.j] = block + self.sid[m.j]
        else:
            # 待避線 j の先頭 k 両 -> 出発線 i の末尾
            block = self.sid[m.j][:m.k]
            del self.sid[m.j][:m.k]
            self.dep[m.i].extend(block)

    def valid_move(self, m: Move) -> bool:
        if not (0 <= m.i < R and 0 <= m.j < R):
            return False
        if m.k <= 0:
            return False

        if m.type == 0:
            movable = len(self.dep[m.i]) - self.fixed_len[m.i]
            if movable < m.k:
                return False
            if len(self.sid[m.j]) + m.k > 20:
                return False
        else:
            if len(self.sid[m.j]) < m.k:
                return False
            if len(self.dep[m.i]) + m.k > 15:
                return False

        return True

    def normalize_fixed(self):
        changed = True

        while changed:
            changed = False

            for i in range(R):
                while (
                    self.fixed_len[i] < 10
                    and len(self.dep[i]) > self.fixed_len[i]
                    and self.dep[i][self.fixed_len[i]] == 10 * i + self.fixed_len[i]
                ):
                    self.fixed_len[i] += 1
                    changed = True

    def done(self) -> bool:
        for i in range(R):
            if self.fixed_len[i] != 10:
                return False
            if len(self.dep[i]) != 10:
                return False
            for c in range(10):
                if self.dep[i][c] != 10 * i + c:
                    return False
        return True

    def find_car(self, x):
        # 確定済み prefix は動かさないので探索対象外
        for i in range(R):
            for p in range(self.fixed_len[i], len(self.dep[i])):
                if self.dep[i][p] == x:
                    return 0, i, p

        for j in range(R):
            for p in range(len(self.sid[j])):
                if self.sid[j][p] == x:
                    return 1, j, p

        return -1, -1, -1

    def target_of(self, x):
        return x // 10

    def choose_siding_for_block(self, block):
        tg = self.target_of(block[-1])

        same_group = all(self.target_of(x) == tg for x in block)

        best_j = -1
        best_score = -10**18

        for j in range(R):
            free_space = 20 - len(self.sid[j])
            if free_space < len(block):
                continue

            score = free_space * 10

            if same_group and j == tg:
                score += 500

            if self.sid[j]:
                front = self.sid[j][0]
                if self.target_of(front) == tg:
                    score += 100

            if self.policy == 1:
                score -= abs(j - tg) * 5
            if self.policy == 2:
                score += 300 if j == tg else 0
            if self.policy == 3:
                score += self.rng.randint(0, 50)

            if score > best_score:
                best_score = score
                best_j = j

        return best_j

    def generate_candidates(self):
        self.normalize_fixed()

        cs = []

        # 1. 待避線先頭に次に必要な車両があれば戻す
        for i in range(R):
            if self.fixed_len[i] >= 10:
                continue
            if len(self.dep[i]) != self.fixed_len[i]:
                continue

            need = 10 * i + self.fixed_len[i]

            for j in range(R):
                if self.sid[j] and self.sid[j][0] == need:
                    sc = 100000
                    if i == j:
                        sc += 1000
                    if self.policy == 1:
                        sc -= abs(i - j) * 10
                    if self.policy == 3:
                        sc += self.rng.randint(0, 200)

                    cs.append(Cand(Move(1, i, j, 1), sc))

        # 2. 出発線の未確定 suffix を待避線へ逃がす
        for i in range(R):
            temp = len(self.dep[i]) - self.fixed_len[i]
            if temp <= 0:
                continue

            max_k = min(temp, 10)

            for k in range(max_k, 0, -1):
                block = self.dep[i][-k:]
                j = self.choose_siding_for_block(block)
                if j == -1:
                    continue

                same = all(self.target_of(x) == self.target_of(block[0]) for x in block)

                sc = 2000 + 80 * k
                if same:
                    sc += 300
                if j == self.target_of(block[-1]):
                    sc += 300
                if self.policy == 2:
                    sc += k * k * 10
                if self.policy == 3:
                    sc += self.rng.randint(0, 100)

                cs.append(Cand(Move(0, i, j, k), sc))
                break

        # 3. 待避線内の必要車両を露出させるため、前方blockを出発線へ逃がす
        for goal in range(R):
            if self.fixed_len[goal] >= 10:
                continue
            if len(self.dep[goal]) != self.fixed_len[goal]:
                continue

            need = 10 * goal + self.fixed_len[goal]
            kind, line, pos = self.find_car(need)

            if kind != 1 or pos <= 0:
                continue

            s = line

            for d in range(R):
                if d == goal and self.fixed_len[d] < 10:
                    continue

                free_space = 15 - len(self.dep[d])
                if free_space <= 0:
                    continue

                k = min(pos, free_space)
                if k <= 0:
                    continue

                sc = 1000 + 70 * k
                sc += max(0, 10 - abs(d - s)) * 5

                if self.policy == 1:
                    sc -= abs(d - s) * 5
                if self.policy == 2:
                    sc += free_space * 10
                if self.policy == 3:
                    sc += self.rng.randint(0, 100)

                cs.append(Cand(Move(1, d, s, k), sc))

        # 4. 必要車両が出発線内にある場合、その上の邪魔を除去する
        for goal in range(R):
            if self.fixed_len[goal] >= 10:
                continue

            need = 10 * goal + self.fixed_len[goal]
            kind, d, pos = self.find_car(need)

            if kind != 0:
                continue

            above = len(self.dep[d]) - pos - 1

            if above > 0:
                max_k = min(above, 10)

                for k in range(max_k, 0, -1):
                    block = self.dep[d][-k:]
                    j = self.choose_siding_for_block(block)

                    if j == -1:
                        continue

                    sc = 3000 + 100 * k
                    if self.policy == 3:
                        sc += self.rng.randint(0, 100)

                    cs.append(Cand(Move(0, d, j, k), sc))
                    break
            else:
                # need が末尾にあるが、まだ直接固定できない場合はいったん待避線へ
                if not (d == goal and pos == self.fixed_len[goal]):
                    for j in range(R):
                        if len(self.sid[j]) >= 20:
                            continue

                        sc = 5000
                        if j == goal:
                            sc += 1000
                        if self.policy == 1:
                            sc -= abs(j - goal) * 10
                        if self.policy == 3:
                            sc += self.rng.randint(0, 100)

                        cs.append(Cand(Move(0, d, j, 1), sc))

        return [c for c in cs if self.valid_move(c.move)]

    def select_non_crossing_dp(self, cs):
        by_i = [[] for _ in range(R)]

        for idx, c in enumerate(cs):
            by_i[c.move.i].append(idx)

        NEG = -10**18

        # dp[i][last_j + 1]
        dp = [[NEG] * (R + 1) for _ in range(R + 1)]
        par_last = [[-1] * (R + 1) for _ in range(R + 1)]
        par_cand = [[-2] * (R + 1) for _ in range(R + 1)]

        dp[0][0] = 0  # last_j = -1 を index 0 として扱う

        for i in range(R):
            for last_idx in range(R + 1):
                if dp[i][last_idx] <= NEG // 2:
                    continue

                # この出発線 i では操作しない
                if dp[i][last_idx] > dp[i + 1][last_idx]:
                    dp[i + 1][last_idx] = dp[i][last_idx]
                    par_last[i + 1][last_idx] = last_idx
                    par_cand[i + 1][last_idx] = -1

                last_j = last_idx - 1

                # 出発線 i を使う候補を選ぶ
                for idx in by_i[i]:
                    j = cs[idx].move.j
                    if j <= last_j:
                        continue

                    nj = j + 1
                    val = dp[i][last_idx] + cs[idx].score

                    if val > dp[i + 1][nj]:
                        dp[i + 1][nj] = val
                        par_last[i + 1][nj] = last_idx
                        par_cand[i + 1][nj] = idx

        best_last = 0
        for j in range(1, R + 1):
            if dp[R][j] > dp[R][best_last]:
                best_last = j

        res = []
        cur_last = best_last

        for i in range(R, 0, -1):
            idx = par_cand[i][cur_last]
            prev = par_last[i][cur_last]

            if idx is None or prev == -1:
                break

            if idx >= 0:
                res.append(cs[idx].move)

            cur_last = prev

        res.reverse()
        return res

    def fallback_one_move(self):
        self.normalize_fixed()

        for i in range(R):
            if self.fixed_len[i] >= 10:
                continue

            need = 10 * i + self.fixed_len[i]

            # まず、出発線 i の未確定部分を逃がす
            if len(self.dep[i]) > self.fixed_len[i]:
                k = len(self.dep[i]) - self.fixed_len[i]
                block = self.dep[i][-k:]
                j = self.choose_siding_for_block(block)

                if j != -1:
                    take = min(k, 20 - len(self.sid[j]))
                    m = Move(0, i, j, take)

                    if self.valid_move(m):
                        self.turns.append([m])
                        self.apply_move(m)
                        return True

            kind, line, pos = self.find_car(need)

            # need が待避線にある
            if kind == 1:
                if pos == 0 and len(self.dep[i]) == self.fixed_len[i]:
                    m = Move(1, i, line, 1)

                    if self.valid_move(m):
                        self.turns.append([m])
                        self.apply_move(m)
                        return True

                for d in range(R):
                    if d == i:
                        continue

                    free_space = 15 - len(self.dep[d])
                    if free_space <= 0:
                        continue

                    k = min(pos, free_space)
                    if k <= 0:
                        continue

                    m = Move(1, d, line, k)

                    if self.valid_move(m):
                        self.turns.append([m])
                        self.apply_move(m)
                        return True

            # need が出発線にある
            if kind == 0:
                above = len(self.dep[line]) - pos - 1

                if above > 0:
                    for j in range(R):
                        free_space = 20 - len(self.sid[j])
                        if free_space <= 0:
                            continue

                        m = Move(0, line, j, min(above, free_space))

                        if self.valid_move(m):
                            self.turns.append([m])
                            self.apply_move(m)
                            return True
                else:
                    for j in range(R):
                        if len(self.sid[j]) >= 20:
                            continue

                        m = Move(0, line, j, 1)

                        if self.valid_move(m):
                            self.turns.append([m])
                            self.apply_move(m)
                            return True

        return False

    def run(self):
        self.reset()
        self.normalize_fixed()

        # 初期状態で、正しいprefix以外を一斉に待避線へ逃がす
        first = []

        for i in range(R):
            k = len(self.dep[i]) - self.fixed_len[i]
            if k > 0:
                first.append(Move(0, i, i, k))

        if first:
            self.turns.append(first)
            for m in first:
                self.apply_move(m)

        self.normalize_fixed()

        safety = 0

        while not self.done() and len(self.turns) < 4000 and safety < 10000:
            safety += 1
            self.normalize_fixed()

            cs = self.generate_candidates()
            selected = self.select_non_crossing_dp(cs)

            if not selected:
                ok = self.fallback_one_move()
                if not ok:
                    break
                continue

            for m in selected:
                if not self.valid_move(m):
                    return []

            self.turns.append(selected)

            for m in selected:
                self.apply_move(m)

            self.normalize_fixed()

        self.normalize_fixed()

        if not self.done():
            return []
        if len(self.turns) > 4000:
            return []

        return self.turns


def check_answer(init_dep, turns):
    dep = deepcopy(init_dep)
    sid = [[] for _ in range(R)]

    if len(turns) > 4000:
        return False

    for turn in turns:
        if not turn or len(turn) > R:
            return False

        used_i = [False] * R
        used_j = [False] * R

        for m in turn:
            if m.type not in (0, 1):
                return False
            if not (0 <= m.i < R and 0 <= m.j < R):
                return False
            if m.k <= 0:
                return False
            if used_i[m.i] or used_j[m.j]:
                return False

            used_i[m.i] = True
            used_j[m.j] = True

        for a in range(len(turn)):
            for b in range(a + 1, len(turn)):
                i1, j1 = turn[a].i, turn[a].j
                i2, j2 = turn[b].i, turn[b].j

                if i1 < i2 and not (j1 < j2):
                    return False
                if i2 < i1 and not (j2 < j1):
                    return False

        for m in turn:
            if m.type == 0:
                if len(dep[m.i]) < m.k:
                    return False
                if len(sid[m.j]) + m.k > 20:
                    return False
            else:
                if len(sid[m.j]) < m.k:
                    return False
                if len(dep[m.i]) + m.k > 15:
                    return False

        for m in turn:
            if m.type == 0:
                block = dep[m.i][-m.k:]
                del dep[m.i][-m.k:]
                sid[m.j] = block + sid[m.j]
            else:
                block = sid[m.j][:m.k]
                del sid[m.j][:m.k]
                dep[m.i].extend(block)

    for i in range(R):
        if len(dep[i]) != 10:
            return False
        for c in range(10):
            if dep[i][c] != 10 * i + c:
                return False

    return True


def main():
    input_data = sys.stdin.read().strip().split()
    if not input_data:
        return

    ptr = 0
    _r = int(input_data[ptr])
    ptr += 1

    init_dep = []
    for _ in range(R):
        row = list(map(int, input_data[ptr:ptr + 10]))
        ptr += 10
        init_dep.append(row)

    best = []
    best_t = 10**18

    start = time.time()
    policy = 0

    # Pythonなので試行数は控えめ
    while time.time() - start < 1.7:
        solver = Solver(init_dep, policy)
        res = solver.run()

        if res and check_answer(init_dep, res):
            if len(res) < best_t:
                best_t = len(res)
                best = res

        policy += 1

        if policy >= 12:
            break

    if not best:
        # 失敗時は何も出せない
        return

    print(len(best))
    for turn in best:
        print(len(turn))
        for m in turn:
            print(m.type, m.i, m.j, m.k)


if __name__ == "__main__":
    main()