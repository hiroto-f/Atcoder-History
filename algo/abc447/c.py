S = input().strip()
T = input().strip()

if S.replace("A", "") != T.replace("A", ""):
    print(-1)
    exit()

i = 0
j = 0
operations = 0

while i < len(S) or j < len(T):
    if i < len(S) and j < len(T) and S[i] == T[j]:
        i += 1
        j += 1
        continue

    if i < len(S) and S[i] == "A":
        i += 1
        operations += 1
        continue

    if j < len(T) and T[j] == "A":
        j += 1
        operations += 1
        continue

print(operations)
