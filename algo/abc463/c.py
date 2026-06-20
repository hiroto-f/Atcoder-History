from bisect import bisect_right


def main():
    n = int(input())
    h = []
    l = []

    for _ in range(n):
        hi, li = map(int, input().split())
        h.append(hi)
        l.append(li)

    suffix_max = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        suffix_max[i] = max(suffix_max[i + 1], h[i])

    q = int(input())
    t = list(map(int, input().split()))

    ans = []
    for ti in t:
        first_present = bisect_right(l, ti)
        ans.append(str(suffix_max[first_present]))

    print("\n".join(ans))


if __name__ == "__main__":
    main()
