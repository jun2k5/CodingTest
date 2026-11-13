"""선형 탐색, 이진 탐색(lower/upper bound), 보간 탐색, 파라메트릭 서치."""
import bisect, random


def linear_search(a, x):
    for i, v in enumerate(a):
        if v == x:
            return i
    return -1


def binary_search(a, x):
    """정렬된 a에서 x의 인덱스(아무거나 하나), 없으면 -1."""
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if a[mid] == x:
            return mid
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def lower_bound(a, x):
    """x 이상인 첫 위치. bisect_left와 같다. 구간 [lo, hi)."""
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo


def upper_bound(a, x):
    """x 초과인 첫 위치. bisect_right와 같다."""
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] <= x:
            lo = mid + 1
        else:
            hi = mid
    return lo


def interpolation_search(a, x):
    """값이 고르게 분포한 정렬 배열에서 위치를 비율로 추정. 평균 O(log log n)."""
    lo, hi, steps = 0, len(a) - 1, 0
    while lo <= hi and a[lo] <= x <= a[hi]:
        steps += 1
        if a[hi] == a[lo]:
            pos = lo
        else:
            pos = lo + (x - a[lo]) * (hi - lo) // (a[hi] - a[lo])
        if a[pos] == x:
            return pos, steps
        if a[pos] < x:
            lo = pos + 1
        else:
            hi = pos - 1
    return -1, steps


def parametric_max(lo, hi, ok):
    """ok(v)가 v ≤ 답에서 True, 그 뒤로 False인 단조 조건일 때 True인 최댓값."""
    while lo < hi:
        mid = (lo + hi + 1) // 2      # 올림 중간값: lo = mid 일 때 무한 반복 방지
        if ok(mid):
            lo = mid
        else:
            hi = mid - 1
    return lo


def cut_trees(heights, need):
    """백준 2805 나무 자르기: 절단기 높이 H의 최댓값 (잘린 나무 합 ≥ need)."""
    return parametric_max(0, max(heights), lambda h: sum(t - h for t in heights if t > h) >= need)


if __name__ == "__main__":
    rng = random.Random(11)
    for _ in range(2000):
        a = sorted(rng.randint(0, 30) for _ in range(rng.randint(0, 40)))
        x = rng.randint(-2, 32)
        assert lower_bound(a, x) == bisect.bisect_left(a, x)
        assert upper_bound(a, x) == bisect.bisect_right(a, x)
        i = binary_search(a, x)
        assert (i == -1 and x not in a) or a[i] == x
        assert (linear_search(a, x) == -1) == (x not in a)
        j, _ = interpolation_search(a, x)
        assert (j == -1 and x not in a) or a[j] == x
    print("linear/binary/lower/upper/interpolation: 2000개 입력에서 bisect·in 연산과 일치")

    a = [1, 3, 3, 3, 5, 8]
    print("a =", a, " lower_bound(3) =", lower_bound(a, 3), " upper_bound(3) =", upper_bound(a, 3),
          " 3의 개수 =", upper_bound(a, 3) - lower_bound(a, 3))

    n = 1_000_000
    uniform = list(range(0, 3 * n, 3))
    x = uniform[777_777]
    _, s = interpolation_search(uniform, x)
    import math
    print(f"균등 분포 {n}개: 보간 탐색 {s}단계, 이진 탐색 최대 {math.ceil(math.log2(n + 1))}단계")
    skew = [i * i for i in range(1, 2001)]
    _, s2 = interpolation_search(skew, skew[1500])
    print(f"제곱수 2000개(치우친 분포): 보간 탐색 {s2}단계")

    print("나무 자르기 [20, 15, 10, 17], M=7 ->", cut_trees([20, 15, 10, 17], 7))
    for _ in range(300):
        hs = [rng.randint(1, 50) for _ in range(rng.randint(1, 10))]
        need = rng.randint(1, sum(hs))
        brute = max(h for h in range(0, max(hs) + 1) if sum(t - h for t in hs if t > h) >= need)
        assert cut_trees(hs, need) == brute
    print("파라메트릭 서치: 300개 입력에서 완전 탐색과 일치")
