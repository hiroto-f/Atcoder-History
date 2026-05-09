from bisect import bisect_left, bisect_right

INF = 10**30

N, M = map(int, input().split())
intervals = []
starts = [[] for _ in range(N + 1)]
ends = [[] for _ in range(N + 1)]
exists = set()

for i in range(M):
    l, r = map(int, input().split())
    intervals.append((l, r))
    starts[l].append((r, i))
    ends[r].append((l, i))
    exists.add((l, r))

for i in range(1, N + 1):
    starts[i].sort()
    ends[i].sort()

Q = int(input())
queries = [tuple(map(int, input().split())) for _ in range(Q)]


def count_contained(s, t): # O(M)
    count = 0
    for l, r in intervals:
        if s <= l and r <= t:
            count += 1
            if count >= 2:
                return count
    return count


def start_candidates(s, t):
    arr = starts[s]
    pos = bisect_right(arr, (t, INF))
    return arr[max(0, pos - 2) : pos]


def end_candidates(s, t):
    arr = ends[t]
    pos = bisect_left(arr, (s, -1))
    return arr[pos : pos + 2]


def can(s, t):
    ## O(M)
    if (s, t) in exists and count_contained(s, t) >= 2:
        return True

    ## O(log M)
    for r, id1 in start_candidates(s, t):
        for l, id2 in end_candidates(s, t):
            if id1 != id2 and l <= r + 1:
                return True
    return False


ans = []
for s, t in queries:
    ans.append("Yes" if can(s, t) else "No")

print("\n".join(ans))
