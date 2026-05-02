a_1 = list(map(int, input().split()))
a_2 = list(map(int, input().split()))
a_3 = list(map(int, input().split()))

all = 6 ** 3

cnt = 0
for i in range(6):
    # print(i, "回目")
    if a_1[i] == 4:
        for j in range(6):
            if a_2[j] == 5:
                for k in range(6):
                    if a_3[k] == 6:
                        cnt += 1
            elif a_2[j] == 6:
                for k in range(6):
                    if a_3[k] == 5:
                        cnt += 1
    elif a_1[i] == 5:
        for j in range(6):
            if a_2[j] == 4:
                for k in range(6):
                    if a_3[k] == 6:
                        cnt += 1
            elif a_2[j] == 6:
                for k in range(6):
                    if a_3[k] == 4:
                        cnt += 1
    elif a_1[i] == 6:
        for j in range(6):
            if a_2[j] == 4:
                for k in range(6):
                    if a_3[k] == 5:
                        cnt += 1
            elif a_2[j] == 5:
                for k in range(6):
                    if a_3[k] == 4:
                        cnt += 1

print(cnt / all)
