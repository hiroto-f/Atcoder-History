import heapq

Q = int(input())

trees = []

for _ in range(Q):
    index, h = map(int, input().split())
    if index == 1:
        heapq.heappush(trees, h)
    else:
        while trees and trees[0] <= h:
            heapq.heappop(trees)

    print(len(trees))
