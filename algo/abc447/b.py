from collections import Counter

S = input()
counter = Counter(S)

max_count = max(counter.values())

result = "".join(ch for ch in S if counter[ch] != max_count)
print(result)