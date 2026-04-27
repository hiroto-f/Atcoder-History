from collections import deque
T = int(input())

ans = []

for t  in range(T):
    N, D = map(int, input().split())
    A = list(map(int, input().split()))
    B = list(map(int, input().split()))

    eggs_left = deque() ## [卵の数, 何日経過したか]
    total = 0

    for n in range(N):
        a = A[n]
        b = B[n]
        if n == 0:
            # print("n==0", "t", t, "a", a, "b", b)
            eggs_left.append([a-b, 0])
            # print("after", eggs_left)
            total += a - b
        else:
            eggs_left.append([a, n])
            total += a - b
            while b > 0:
                egg = eggs_left.popleft()
                if egg[0] > b:
                    eggs_left.appendleft([egg[0]-b, egg[1]])
                    break
                else:
                    b -= egg[0]
        
        # if eggs_left and eggs_left[0][1] >= D:
        #         eggs_left.popleft()
        #         total -= eggs_left[0][0]
        # for egg in eggs_left:
        #     egg[1] += 1
        if eggs_left and (n - eggs_left[0][1] >= D):
            total -= eggs_left[0][0]
            eggs_left.popleft()
        
        # print("total", total)
    
    # print("t", t, "n", n, eggs_left)
    ans.append(total)


for a in ans:    
    print(a)
