import sys
import time


DEBUG = False
DEP_CAP = 15
REF_CAP = 20
TIME_LIMIT = 1.45


class Random:
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


def find_car(refs, x):
    for j, line in enumerate(refs):
        for p, v in enumerate(line):
            if v == x:
                return j, p
    raise RuntimeError("car not found")


def choose_buffer(deps, out, rng, mode):
    candidates = []
    for i, line in enumerate(deps):
        if i == out:
            continue
        spare = DEP_CAP - len(line)
        if spare > 0:
            candidates.append((spare, i))
    if not candidates:
        return -1, 0

    candidates.sort(reverse=True)
    if mode == 0:
        spare, i = candidates[0]
    elif mode == 1:
        top = candidates[: min(3, len(candidates))]
        spare, i = top[rng.randrange(len(top))]
    elif mode == 2:
        spare, i = min(candidates, key=lambda x: (abs(x[1] - out), -x[0]))
    else:
        spare, i = candidates[rng.randrange(len(candidates))]
    return i, spare


def build_operations(r, y, round_orders, rng, buffer_mode):
    """全出発線の prefix を少しずつ伸ばす逐次操作列を作る。

    各出発線を1本ずつ完成させるのではなく、出発線0,1,...,R-1の
    次に必要な車両を順番に拾っていく。生成後に同時移動スケジューラへ
    通すことで、別々の線に関する操作が同じターンへまとまりやすくなる。
    """

    deps = [row[:] for row in y]
    refs = [[] for _ in range(r)]
    ops = []

    for i in range(r):
        k = len(deps[i])
        if k:
            block = deps[i][-k:]
            del deps[i][-k:]
            refs[i] = block + refs[i]
            ops.append((0, i, i, k))

    fixed = [0] * r
    round_idx = 0
    while min(fixed) < 10:
        progressed = False
        order = round_orders[round_idx % len(round_orders)]
        round_idx += 1
        for out in order:
            if fixed[out] >= 10:
                continue
            x = 10 * out + fixed[out]
            src, pos = find_car(refs, x)

            block_len = 1
            while (
                fixed[out] + block_len < 10
                and pos + block_len < len(refs[src])
                and refs[src][pos + block_len] == x + block_len
            ):
                block_len += 1

            chunks = []
            remain = pos
            while remain:
                buf, spare = choose_buffer(deps, out, rng, buffer_mode)
                if spare <= 0:
                    raise RuntimeError("no buffer capacity")
                k = min(spare, remain)
                moving = refs[src][:k]
                del refs[src][:k]
                deps[buf].extend(moving)
                ops.append((1, buf, src, k))
                chunks.append((buf, k))
                remain -= k

            moving = refs[src][:block_len]
            del refs[src][:block_len]
            deps[out].extend(moving)
            ops.append((1, out, src, block_len))
            fixed[out] += block_len
            progressed = True

            for buf, k in reversed(chunks):
                moving = deps[buf][-k:]
                del deps[buf][-k:]
                refs[src] = moving + refs[src]
                ops.append((0, buf, src, k))

        if not progressed:
            raise RuntimeError("prefix builder stalled")

    return ops


def next_block_info(refs, fixed, out):
    x = 10 * out + fixed[out]
    src, pos = find_car(refs, x)
    block_len = 1
    while (
        fixed[out] + block_len < 10
        and pos + block_len < len(refs[src])
        and refs[src][pos + block_len] == x + block_len
    ):
        block_len += 1
    return src, pos, block_len


def move_next_block(deps, refs, ops, fixed, out, rng, buffer_mode):
    src, pos, block_len = next_block_info(refs, fixed, out)

    chunks = []
    remain = pos
    while remain:
        buf, spare = choose_buffer(deps, out, rng, buffer_mode)
        if spare <= 0:
            raise RuntimeError("no buffer capacity")
        k = min(spare, remain)
        moving = refs[src][:k]
        del refs[src][:k]
        deps[buf].extend(moving)
        ops.append((1, buf, src, k))
        chunks.append((buf, k))
        remain -= k

    moving = refs[src][:block_len]
    del refs[src][:block_len]
    deps[out].extend(moving)
    ops.append((1, out, src, block_len))
    fixed[out] += block_len

    for buf, k in reversed(chunks):
        moving = deps[buf][-k:]
        del deps[buf][-k:]
        refs[src] = moving + refs[src]
        ops.append((0, buf, src, k))


def build_operations_dynamic(r, y, rng, buffer_mode, select_mode):
    """その時点で拾いやすい prefix を1つずつ伸ばす候補生成。"""

    deps = [row[:] for row in y]
    refs = [[] for _ in range(r)]
    ops = []

    for i in range(r):
        k = len(deps[i])
        if k:
            block = deps[i][-k:]
            del deps[i][-k:]
            refs[i] = block + refs[i]
            ops.append((0, i, i, k))

    fixed = [0] * r
    while min(fixed) < 10:
        candidates = []
        for out in range(r):
            if fixed[out] >= 10:
                continue
            src, pos, block_len = next_block_info(refs, fixed, out)
            candidates.append((pos, -block_len, src, out))

        if select_mode == 0:
            _, _, _, out = min(candidates)
        elif select_mode == 1:
            _, _, _, out = min(candidates, key=lambda x: (x[1], x[0], x[3]))
        elif select_mode == 2:
            candidates.sort()
            top = candidates[: min(3, len(candidates))]
            _, _, _, out = top[rng.randrange(len(top))]
        elif select_mode == 3:
            candidates.sort(key=lambda x: (x[2], x[0], x[3]))
            _, _, _, out = candidates[0]
        else:
            candidates.sort(key=lambda x: (x[0] + rng.randrange(4), x[1], x[3]))
            _, _, _, out = candidates[0]

        move_next_block(deps, refs, ops, fixed, out, rng, buffer_mode)

    return ops


def shuffled_order(r, rng):
    order = list(range(r))
    for i in range(r - 1, 0, -1):
        j = rng.randrange(i + 1)
        order[i], order[j] = order[j], order[i]
    return order


def schedule_operations(r, ops):
    """線ごとの順序を保ちながら、非交差な操作を同一ターンへ詰める。"""

    n = len(ops)
    graph = [[] for _ in range(n)]
    indeg = [0] * n
    last_dep = [-1] * r
    last_ref = [-1] * r

    for idx, (_, i, j, _) in enumerate(ops):
        prev = last_dep[i]
        if prev != -1:
            graph[prev].append(idx)
            indeg[idx] += 1
        prev = last_ref[j]
        if prev != -1:
            graph[prev].append(idx)
            indeg[idx] += 1
        last_dep[i] = idx
        last_ref[j] = idx

    priority = [1] * n
    for idx in range(n - 1, -1, -1):
        if graph[idx]:
            priority[idx] = 1 + max(priority[nxt] for nxt in graph[idx])

    done = [False] * n
    done_count = 0
    turns = []

    while done_count < n:
        ready = [idx for idx in range(n) if not done[idx] and indeg[idx] == 0]
        best_mask = 0
        best_score = (-1, -1, 0)
        m = len(ready)

        for mask in range(1, 1 << m):
            used_dep = set()
            used_ref = set()
            pairs = []
            index_sum = 0
            priority_sum = 0
            ok = True
            for bit in range(m):
                if not ((mask >> bit) & 1):
                    continue
                idx = ready[bit]
                _, i, j, _ = ops[idx]
                if i in used_dep or j in used_ref:
                    ok = False
                    break
                used_dep.add(i)
                used_ref.add(j)
                pairs.append((i, j))
                index_sum += idx
                priority_sum += priority[idx]
            if not ok:
                continue
            pairs.sort()
            for p in range(1, len(pairs)):
                if pairs[p - 1][1] >= pairs[p][1]:
                    ok = False
                    break
            if not ok:
                continue
            score = (len(pairs), priority_sum, -index_sum)
            if score > best_score:
                best_score = score
                best_mask = mask

        if best_mask == 0:
            raise RuntimeError("scheduler deadlock")

        selected = [ready[bit] for bit in range(m) if (best_mask >> bit) & 1]
        selected.sort(key=lambda idx: (ops[idx][1], ops[idx][2]))
        turns.append([ops[idx] for idx in selected])

        for idx in selected:
            done[idx] = True
            done_count += 1
            for nxt in graph[idx]:
                indeg[nxt] -= 1

    return turns


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
            if pairs[idx - 1][0] >= pairs[idx][0] or pairs[idx - 1][1] >= pairs[idx][1]:
                return False
    for i in range(r):
        if deps[i] != list(range(10 * i, 10 * i + 10)):
            return False
    return True


def make_round_orders(r, rng, pattern):
    if pattern == 0:
        return [list(range(r))]
    if pattern == 1:
        return [list(reversed(range(r)))]
    if pattern == 2:
        base = shuffled_order(r, rng)
        return [base]
    if pattern == 3:
        base = shuffled_order(r, rng)
        return [base, list(reversed(base))]
    if pattern == 4:
        base = shuffled_order(r, rng)
        return [base[s:] + base[:s] for s in range(r)]
    return [shuffled_order(r, rng) for _ in range(10)]


def solve(r, y):
    start = time.perf_counter()
    rng = Random(1)

    best_turns = None
    best_count = 10**9
    attempt = 0

    while True:
        pattern = attempt % 6
        buffer_mode = (attempt // 6) % 4

        try:
            round_orders = make_round_orders(r, rng, pattern)
            ops = build_operations(r, y, round_orders, rng, buffer_mode)
            turns = schedule_operations(r, ops)
        except RuntimeError:
            turns = None

        if turns is not None and len(turns) < best_count:
            best_turns = turns
            best_count = len(turns)

        attempt += 1
        if attempt & 7 == 0 and time.perf_counter() - start >= TIME_LIMIT:
            break

    return best_turns


def main():
    first = sys.stdin.buffer.readline()
    if not first:
        return
    r = int(first)
    y = [list(map(int, sys.stdin.buffer.readline().split())) for _ in range(r)]

    turns = solve(r, y)
    if DEBUG:
        assert validate_output(r, y, turns)

    out = [str(len(turns))]
    for turn in turns:
        out.append(str(len(turn)))
        for op in turn:
            out.append("{} {} {} {}".format(*op))
    sys.stdout.write("\n".join(out))


if __name__ == "__main__":
    main()
