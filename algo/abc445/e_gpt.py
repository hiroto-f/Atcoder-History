import sys
from array import array

MOD = 998244353

# ---------- SPF (smallest prime factor) sieve ----------
def build_spf(n: int):
    spf = array('I', [0]) * (n + 1)
    primes = []
    spf[0] = 0
    if n >= 1:
        spf[1] = 1
    # linear sieve
    for i in range(2, n + 1):
        if spf[i] == 0:
            spf[i] = i
            primes.append(i)
        si = spf[i]
        for p in primes:
            ip = i * p
            if ip > n:
                break
            spf[ip] = p
            if p == si:
                break
    return spf

def factorize(x: int, spf):
    res = []
    while x > 1:
        p = spf[x]
        c = 0
        while x % p == 0:
            x //= p
            c += 1
        res.append((p, c))
    return res

# ---------- Main ----------
def main():
    data = list(map(int, sys.stdin.buffer.read().split()))
    it = iter(data)
    T = next(it)

    # read all testcases first to know maxA
    tests = []
    maxA = 1
    for _ in range(T):
        n = next(it)
        arr = [next(it) for _ in range(n)]
        if arr:
            m = max(arr)
            if m > maxA:
                maxA = m
        tests.append(arr)

    spf = build_spf(maxA)

    out_lines = []
    mod = MOD

    for A in tests:
        n = len(A)

        # per prime: max exp, second max exp, count of max
        maxe = {}
        sece = {}
        cntmax = {}

        facts = [None] * n

        for i, x in enumerate(A):
            fx = factorize(x, spf)
            facts[i] = fx
            for p, e in fx:
                me = maxe.get(p, 0)
                if e > me:
                    sece[p] = me
                    maxe[p] = e
                    cntmax[p] = 1
                elif e == me:
                    cntmax[p] = cntmax.get(p, 0) + 1
                else:
                    sm = sece.get(p, 0)
                    if e > sm:
                        sece[p] = e

        # L = lcm(all) mod MOD
        L = 1
        pow_p_max = {}
        for p, e in maxe.items():
            v = pow(p, e, mod)
            pow_p_max[p] = v
            L = (L * v) % mod

        # for primes where excluding the unique max-holder reduces exponent:
        # ratio[p] = p^sece / p^maxe (mod)
        ratio = {}
        for p, e in maxe.items():
            if cntmax.get(p, 0) == 1:
                s = sece.get(p, 0)
                if s != e:
                    ratio[p] = (pow(p, s, mod) * pow(pow_p_max[p], mod - 2, mod)) % mod

        # answer for each k
        ans = []
        for fx in facts:
            r = L
            for p, e in fx:
                if cntmax.get(p, 0) == 1 and e == maxe[p]:
                    r = (r * ratio[p]) % mod
            ans.append(str(r))

        # AtCoder形式想定: 1テストケースにつきN個を1行で出力
        out_lines.append(" ".join(ans))

    sys.stdout.write("\n".join(out_lines))

if __name__ == "__main__":
    main()