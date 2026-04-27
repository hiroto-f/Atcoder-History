import sys


DEP_CAP = 15
REF_CAP = 20


def find_car(refs, x):
    for j, line in enumerate(refs):
        for p, v in enumerate(line):
            if v == x:
                return j, p
    raise RuntimeError("car not found")


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


def build_operations(r, y, order):
    """既存の構築法で、1操作ずつの逐次操作列を作る。"""

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
                ops.append((1, buf, src, k))
                chunks.append((buf, k))
                remain -= k

            moving = refs[src][:block_len]
            del refs[src][:block_len]
            deps[out].extend(moving)
            ops.append((1, out, src, block_len))
            done[out] += block_len

            for buf, k in reversed(chunks):
                moving = deps[buf][-k:]
                del deps[buf][-k:]
                refs[src] = moving + refs[src]
                ops.append((0, buf, src, k))

    return ops


def schedule_operations(r, ops, collect_turns):
    """線ごとの順序を守りつつ、非交差な操作を同一ターンに詰める。"""

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

    done = [False] * n
    done_count = 0
    turn_count = 0
    turns = []

    while done_count < n:
        ready = [idx for idx in range(n) if not done[idx] and indeg[idx] == 0]
        best_mask = 0
        best_score = (-1, 0)
        m = len(ready)

        for mask in range(1, 1 << m):
            used_dep = set()
            used_ref = set()
            pairs = []
            index_sum = 0
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
            if not ok:
                continue
            pairs.sort()
            for p in range(1, len(pairs)):
                if pairs[p - 1][1] >= pairs[p][1]:
                    ok = False
                    break
            if not ok:
                continue
            score = (len(pairs), -index_sum)
            if score > best_score:
                best_score = score
                best_mask = mask

        if best_mask == 0:
            raise RuntimeError("scheduler deadlock")

        selected = [ready[bit] for bit in range(m) if (best_mask >> bit) & 1]
        selected.sort(key=lambda idx: (ops[idx][1], ops[idx][2]))
        if collect_turns:
            turns.append([ops[idx] for idx in selected])
        turn_count += 1

        for idx in selected:
            done[idx] = True
            done_count += 1
            for nxt in graph[idx]:
                indeg[nxt] -= 1

    if collect_turns:
        return turn_count, turns
    return turn_count, None


def build_solution(r, y, order, collect_turns):
    ops = build_operations(r, y, order)
    return schedule_operations(r, ops, collect_turns)


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


def main():
    first = sys.stdin.buffer.readline()
    if not first:
        return
    r = int(first)
    y = []
    for _ in range(r):
        y.append(list(map(int, sys.stdin.buffer.readline().split())))

    order = list(range(r))
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
