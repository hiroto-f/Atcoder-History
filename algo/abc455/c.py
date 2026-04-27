from collections import Counter


N, K = map(int, input().split())
A = list(map(int, input().split()))

count = Counter(A)
total = sum(A)
savings = sorted((value * freq for value, freq in count.items()), reverse=True)

print(total - sum(savings[:K]))
