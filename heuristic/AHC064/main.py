import math
import sys
import time


DEP_CAP = 15
REF_CAP = 20
TIME_LIMIT = 1.65


class Random:
    """軽量な疑似乱数生成器。

    同じ seed からは常に同じ乱数列を生成するので、提出結果を再現しやすい。

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


def find_car(refs, x):
    for j, line in enumerate(refs):
        for p, v in enumerate(line):
            if v == x:
                return j, p
    raise RuntimeError("car not found")


def add_turn(turns, op, collect_ops):
    if collect_ops:
        turns.append([op])


def choose_buffer(deps, out):
    best = -1
    best_spare = -1
    for i, line in enumerate(deps):
        if i == out:
            continue
        spare = DEP_CAP - len(line)
        if spare > best_spare:
            best = i
            best_spare = spare
    return best, best_spare


def build_solution(r, y, order, collect_ops):
    deps = [row[:] for row in y]
    refs = [[] for _ in range(r)]
    turns = []
    turn_count = 0

    first_turn = []
    for i in range(r):
        k = len(deps[i])
        if k:
            block = deps[i][-k:]
            del deps[i][-k:]
            refs[i] = block + refs[i]
            first_turn.append((0, i, i, k))
    if first_turn:
        if collect_ops:
            turns.append(first_turn)
        turn_count += 1

    done = [0] * r
    for out in order:
        while done[out] < 10:
            x = 10 * out + done[out]
            src, pos = find_car(refs, x)

            block_len = 1
            while (
                done[out] + block_len < 10
                and pos + block_len < len(refs[src])
                and refs[src][pos + block_len] == x + block_len
            ):
                block_len += 1

            chunks = []
            remain = pos
            while remain:
                buf, spare = choose_buffer(deps, out)
                if spare <= 0:
                    raise RuntimeError("no buffer capacity")
                k = min(spare, remain)
                moving = refs[src][:k]
                del refs[src][:k]
                deps[buf].extend(moving)
                add_turn(turns, (1, buf, src, k), collect_ops)
                turn_count += 1
                chunks.append((buf, k))
                remain -= k

            moving = refs[src][:block_len]
            del refs[src][:block_len]
            deps[out].extend(moving)
            add_turn(turns, (1, out, src, block_len), collect_ops)
            turn_count += 1
            done[out] += block_len

            for buf, k in reversed(chunks):
                moving = deps[buf][-k:]
                del deps[buf][-k:]
                refs[src] = moving + refs[src]
                add_turn(turns, (0, buf, src, k), collect_ops)
                turn_count += 1

    if collect_ops:
        for i in range(r):
            target = list(range(10 * i, 10 * i + 10))
            assert deps[i] == target
            assert len(deps[i]) <= DEP_CAP
            assert len(refs[i]) <= REF_CAP
        assert sum(len(line) for line in refs) == 0
    return turn_count, turns


def anneal_order(r, y):
    rng = Random(1)
    start = time.perf_counter()

    cur = list(range(r))
    cur_score, _ = build_solution(r, y, cur, False)
    best = cur[:]
    best_score = cur_score

    # A few randomized starts help because the search space is only 10!.
    for _ in range(64):
        cand = list(range(r))
        for i in range(r - 1, 0, -1):
            j = rng.randrange(i + 1)
            cand[i], cand[j] = cand[j], cand[i]
        score, _ = build_solution(r, y, cand, False)
        if score < best_score:
            best = cand[:]
            best_score = score
        if score < cur_score:
            cur = cand
            cur_score = score

    start_temp = 8.0
    end_temp = 0.05
    loop = 0
    while True:
        loop += 1
        if loop & 127 == 0:
            elapsed = time.perf_counter() - start
            if elapsed >= TIME_LIMIT:
                break
            progress = elapsed / TIME_LIMIT
            temp = start_temp * ((end_temp / start_temp) ** progress)
        elif loop == 1:
            temp = start_temp

        cand = cur[:]
        a = rng.randrange(r)
        b = rng.randrange(r)
        if a > b:
            a, b = b, a
        if a == b:
            continue
        if rng.randrange(3) == 0:
            cand[a : b + 1] = reversed(cand[a : b + 1])
        else:
            cand[a], cand[b] = cand[b], cand[a]

        score, _ = build_solution(r, y, cand, False)
        diff = score - cur_score
        if diff <= 0 or rng.random() < math.exp(-diff / temp):
            cur = cand
            cur_score = score
            if score < best_score:
                best = cand[:]
                best_score = score

    return best


def validate_output(r, y, turns):
    deps = [row[:] for row in y]
    refs = [[] for _ in range(r)]
    if len(turns) > 4000:
        return False
    for turn in turns:
        used_dep = set()
        used_ref = set()
        pairs = []
        for typ, i, j, k in turn:
            if not (0 <= i < r and 0 <= j < r and k >= 1):
                return False
            if i in used_dep or j in used_ref:
                return False
            used_dep.add(i)
            used_ref.add(j)
            pairs.append((i, j))
            if typ == 0:
                if len(deps[i]) < k or len(refs[j]) + k > REF_CAP:
                    return False
                block = deps[i][-k:]
                del deps[i][-k:]
                refs[j] = block + refs[j]
            elif typ == 1:
                if len(refs[j]) < k or len(deps[i]) + k > DEP_CAP:
                    return False
                block = refs[j][:k]
                del refs[j][:k]
                deps[i].extend(block)
            else:
                return False
        pairs.sort()
        for idx in range(1, len(pairs)):
            if not (pairs[idx - 1][0] < pairs[idx][0] and pairs[idx - 1][1] < pairs[idx][1]):
                return False
    for i in range(r):
        if deps[i] != list(range(10 * i, 10 * i + 10)):
            return False
    return True


def main():
    first = sys.stdin.buffer.readline()
    if not first:
        return
    r = int(first)
    y = []
    for _ in range(r):
        y.append(list(map(int, sys.stdin.buffer.readline().split())))

    order = anneal_order(r, y)
    _, turns = build_solution(r, y, order, True)
    assert validate_output(r, y, turns)

    out = [str(len(turns))]
    for turn in turns:
        out.append(str(len(turn)))
        for op in turn:
            out.append("{} {} {} {}".format(*op))
    sys.stdout.write("\n".join(out))


if __name__ == "__main__":
    main()
