S = input()

all_a_index = [idx for idx, ch in enumerate(S) if ch == "A"]   # [0, 3, 5, 7, 10]
all_b_index = [idx for idx, ch in enumerate(S) if ch == "B"]   
all_c_index = [idx for idx, ch in enumerate(S) if ch == "C"]   

ans = 0
b_index, c_index = 0, 0

for a_index in all_a_index:
    while b_index < len(all_b_index) and all_b_index[b_index] <= a_index:
        b_index += 1
    if b_index == len(all_b_index):
        break

    while c_index < len(all_c_index) and all_c_index[c_index] <= all_b_index[b_index]:
        c_index += 1
    if c_index == len(all_c_index):
        break

    ## これをしないと同じ場所で止まる可能性がある
    b_index += 1
    c_index += 1
    ans += 1

print(ans)
