T, X = map(int, input().split())
A = list(map(int, input().split()))

saved_data = []
previous_saved_data = 0

for i in range(T+1):
    if i == 0:
        saved_data.append([i, A[i]])
        previous_saved_data = A[i]
    else:
        # print(i, A[i], previous_saved_data)
        if abs(A[i] - previous_saved_data) >= X:
            saved_data.append([i, A[i]])
            previous_saved_data = A[i]

for i in range(len(saved_data)):
    print(saved_data[i][0], saved_data[i][1])

