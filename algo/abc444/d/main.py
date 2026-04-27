N = int(input())
A = list(map(int, input().split()))

A.sort()
max_a = max(A)

extra = 30
digits = [0] * (max_a + extra)

j = 0
for i in range(max_a):
    while j < N and A[j] <= i:
        j += 1
    digits[i] = N - j

for i in range(len(digits) - 1):
    digits[i + 1] += digits[i] // 10
    digits[i] %= 10 # あまり

while len(digits) > 1 and digits[-1] == 0:
    digits.pop()

print(''.join(map(str, reversed(digits))))
