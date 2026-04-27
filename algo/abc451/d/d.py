from collections import deque


N = int(input())


def build_automaton(max_length):
    powers = []
    value = 1
    while len(str(value)) <= max_length:
        powers.append(str(value))
        value *= 2

    trie = [{}]
    is_terminal = [False]

    for power in powers:
        node = 0
        for digit in power:
            if digit not in trie[node]:
                trie[node][digit] = len(trie)
                trie.append({})
                is_terminal.append(False)
            node = trie[node][digit]
        is_terminal[node] = True

    start_state = frozenset([0])
    queue = deque([start_state])
    state_id = {start_state: 0}
    transitions = []
    is_accepted = []

    while queue:
        state = queue.popleft()
        state_index = state_id[state]

        while len(transitions) <= state_index:
            transitions.append({})
            is_accepted.append(any(is_terminal[node] for node in state))

        for digit in "0123456789":
            next_state = set()
            reached_terminal = False

            for node in state:
                next_node = trie[node].get(digit)
                if next_node is None:
                    continue
                next_state.add(next_node)
                if is_terminal[next_node]:
                    reached_terminal = True

            if reached_terminal:
                next_state.add(0)

            if not next_state:
                continue

            frozen_next_state = frozenset(next_state)
            if frozen_next_state not in state_id:
                state_id[frozen_next_state] = len(state_id)
                queue.append(frozen_next_state)

            transitions[state_index][digit] = state_id[frozen_next_state]

    return transitions, is_accepted


def count_by_length(transitions, is_accepted, max_length, limit):
    state_count = len(transitions)
    current = [0] * state_count
    current[0] = 1
    counts = []

    for length in range(1, max_length + 1):
        next_counts = [0] * state_count
        digits = "123456789" if length == 1 else "0123456789"

        for state, ways in enumerate(current):
            if ways == 0:
                continue
            for digit in digits:
                next_state = transitions[state].get(digit)
                if next_state is None:
                    continue
                next_counts[next_state] += ways
                if next_counts[next_state] > limit:
                    next_counts[next_state] = limit

        total = 0
        for state, accepted in enumerate(is_accepted):
            if accepted:
                total += next_counts[state]
                if total > limit:
                    total = limit
                    break

        counts.append(total)
        current = next_counts

    return counts


def build_suffix_counts(transitions, is_accepted, length, limit):
    state_count = len(transitions)
    suffix_counts = [[0] * state_count for _ in range(length + 1)]

    for state in range(state_count):
        suffix_counts[0][state] = 1 if is_accepted[state] else 0

    for remaining in range(1, length + 1):
        for state in range(state_count):
            total = 0
            for next_state in transitions[state].values():
                total += suffix_counts[remaining - 1][next_state]
                if total > limit:
                    total = limit
                    break
            suffix_counts[remaining][state] = total

    return suffix_counts


length = 1
while True:
    transitions, is_accepted = build_automaton(length)
    counts = count_by_length(transitions, is_accepted, length, N)
    if sum(counts) >= N:
        break
    length += 1

k = N - sum(counts[:-1])
suffix_counts = build_suffix_counts(transitions, is_accepted, length, k)

answer = []
state = 0

for position in range(length):
    digits = "123456789" if position == 0 else "0123456789"
    remaining = length - position - 1

    for digit in digits:
        next_state = transitions[state].get(digit)
        if next_state is None:
            continue

        count = suffix_counts[remaining][next_state]
        if k > count:
            k -= count
            continue

        answer.append(digit)
        state = next_state
        break

print("".join(answer))
