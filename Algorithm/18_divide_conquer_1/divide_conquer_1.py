"""분할 정복 ①: 거듭제곱, 최근접 점쌍, 퀵셀렉트, 역순 쌍 세기."""
import math, random


def power(a, n, mod=None):
    """a^n을 O(log n) 곱셈으로. n이 짝수면 (a^(n/2))^2."""
    if n == 0:
        return 1 if mod is None else 1 % mod
    half = power(a, n // 2, mod)
    r = half * half
    if n % 2:
        r *= a
    return r if mod is None else r % mod


def closest_pair(points):
    """최근접 두 점 사이 거리. x로 정렬 후 분할, 가운데 띠에서 y순으로 최대 7개만 비교."""
    px = sorted(points)

    def solve(p):
        n = len(p)
        if n <= 3:
            return min((math.dist(p[i], p[j]) for i in range(n) for j in range(i + 1, n)), default=float("inf")), sorted(p, key=lambda q: q[1])
        mid = n // 2
        mx = p[mid][0]
        dl, yl = solve(p[:mid])
        dr, yr = solve(p[mid:])
        d = min(dl, dr)
        ys, i, j = [], 0, 0                     # y 기준 병합(병합 정렬처럼)
        while i < len(yl) and j < len(yr):
            if yl[i][1] <= yr[j][1]: ys.append(yl[i]); i += 1
            else: ys.append(yr[j]); j += 1
        ys += yl[i:] + yr[j:]
        strip = [q for q in ys if abs(q[0] - mx) < d]
        for a in range(len(strip)):
            for b in range(a + 1, min(a + 8, len(strip))):   # 띠 안에서는 위로 최대 7개만 보면 된다
                if strip[b][1] - strip[a][1] >= d:
                    break
                d = min(d, math.dist(strip[a], strip[b]))
        return d, ys

    return solve(px)[0]


def quickselect(a, k):
    """k번째로 작은 값(0부터). 평균 O(n)."""
    a = a[:]
    lo, hi = 0, len(a) - 1
    while True:
        if lo == hi:
            return a[lo]
        p = random.randint(lo, hi)
        a[p], a[hi] = a[hi], a[p]
        pivot, i = a[hi], lo
        for j in range(lo, hi):
            if a[j] < pivot:
                a[i], a[j] = a[j], a[i]; i += 1
        a[i], a[hi] = a[hi], a[i]
        if k == i:
            return a[i]
        if k < i:
            hi = i - 1                         # 한쪽만 따라간다: 퀵 정렬과 다른 점
        else:
            lo = i + 1


def count_inversions(a):
    """i < j 이면서 a[i] > a[j]인 쌍의 수. 병합하면서 센다."""
    if len(a) <= 1:
        return 0, a[:]
    mid = len(a) // 2
    cl, l = count_inversions(a[:mid])
    cr, r = count_inversions(a[mid:])
    out, i, j, c = [], 0, 0, cl + cr
    while i < len(l) and j < len(r):
        if l[i] <= r[j]:
            out.append(l[i]); i += 1
        else:
            out.append(r[j]); j += 1
            c += len(l) - i                    # 왼쪽에 남은 원소는 모두 r[j]보다 크다
    out += l[i:] + r[j:]
    return c, out


if __name__ == "__main__":
    rng = random.Random(59)
    for _ in range(500):
        a, n, m = rng.randint(-9, 9), rng.randint(0, 40), rng.randint(1, 1000)
        assert power(a, n) == a ** n and power(a, n, m) == pow(a, n, m)
    print("거듭제곱: 500개 입력에서 ** / pow와 일치")
    calls = [0]
    def counted(a, n):
        calls[0] += 1
        if n == 0: return 1
        h = counted(a, n // 2); r = h * h
        return r * a if n % 2 else r
    counted(3, 10**6)
    print("3^1000000 계산에 든 재귀 호출 수:", calls[0])

    for _ in range(200):
        pts = list({(rng.randint(0, 200), rng.randint(0, 200)) for _ in range(rng.randint(2, 80))})
        if len(pts) < 2: continue
        brute = min(math.dist(pts[i], pts[j]) for i in range(len(pts)) for j in range(i + 1, len(pts)))
        assert abs(closest_pair(pts) - brute) < 1e-9
    print("최근접 점쌍: 200개 입력에서 O(n^2) 완전 탐색과 일치")

    for _ in range(500):
        a = [rng.randint(-50, 50) for _ in range(rng.randint(1, 60))]
        k = rng.randrange(len(a))
        assert quickselect(a, k) == sorted(a)[k]
    print("퀵셀렉트: 500개 입력에서 sorted(a)[k]와 일치")

    for _ in range(300):
        a = [rng.randint(0, 20) for _ in range(rng.randint(0, 50))]
        brute = sum(1 for i in range(len(a)) for j in range(i + 1, len(a)) if a[i] > a[j])
        assert count_inversions(a)[0] == brute
    print("역순 쌍 세기: 300개 입력에서 이중 반복문과 일치. [3, 1, 2] ->", count_inversions([3, 1, 2])[0])
