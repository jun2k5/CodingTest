"""병합 정렬과 퀵 정렬."""
import sys, pathlib, random
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


def merge_sort(a):
    """새 리스트를 반환하는 안정 정렬. O(n log n), 추가 공간 O(n)."""
    if len(a) <= 1:
        return a[:]
    mid = len(a) // 2
    left, right = merge_sort(a[:mid]), merge_sort(a[mid:])
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:          # <= 이어야 같은 값의 순서가 유지된다(안정성)
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
    out.extend(left[i:]); out.extend(right[j:])
    return out


def quick_sort(a, lo=0, hi=None):
    """제자리 퀵 정렬 (Lomuto 분할, 무작위 피벗)."""
    if hi is None:
        hi = len(a) - 1
    while lo < hi:
        p = random.randint(lo, hi)
        a[p], a[hi] = a[hi], a[p]
        pivot, i = a[hi], lo
        for j in range(lo, hi):
            if a[j] < pivot:
                a[i], a[j] = a[j], a[i]; i += 1
        a[i], a[hi] = a[hi], a[i]
        # 작은 쪽만 재귀하고 큰 쪽은 반복으로 처리해 재귀 깊이를 O(log n)으로 제한
        if i - lo < hi - i:
            quick_sort(a, lo, i - 1); lo = i + 1
        else:
            quick_sort(a, i + 1, hi); hi = i - 1


def quick_sort_hoare(a, lo=0, hi=None):
    """Hoare 분할: 교환 횟수가 Lomuto보다 적고 중복 값이 많아도 균형이 잘 맞는다."""
    if hi is None:
        hi = len(a) - 1
    if lo >= hi:
        return
    pivot = a[(lo + hi) // 2]
    i, j = lo - 1, hi + 1
    while True:
        i += 1
        while a[i] < pivot: i += 1
        j -= 1
        while a[j] > pivot: j -= 1
        if i >= j: break
        a[i], a[j] = a[j], a[i]
    quick_sort_hoare(a, lo, j)
    quick_sort_hoare(a, j + 1, hi)


def naive_quick_sort_depth(a):
    """첫 원소를 피벗으로 쓰는 단순 퀵 정렬의 최대 재귀 깊이."""
    best = [0]
    def go(x, d):
        best[0] = max(best[0], d)
        if len(x) <= 1: return x
        p = x[0]
        return go([v for v in x[1:] if v < p], d + 1) + [p] + go([v for v in x[1:] if v >= p], d + 1)
    go(a, 0)
    return best[0]


if __name__ == "__main__":
    from _check import check_sort
    check_sort(merge_sort, inplace=False)
    check_sort(quick_sort)
    check_sort(quick_sort_hoare)

    class K:
        """값만 비교하고 원래 순서는 따로 들고 있는 레코드."""
        def __init__(s, r): s.r = r
        def __le__(s, o): return s.r[0] <= o.r[0]
        def __lt__(s, o): return s.r[0] < o.r[0]
        def __gt__(s, o): return s.r[0] > o.r[0]

    rng = random.Random(3)
    recs = [(rng.randint(0, 5), i) for i in range(200)]
    stable = lambda r: all(r[i][1] < r[i + 1][1] for i in range(len(r) - 1) if r[i][0] == r[i + 1][0])
    print("병합 정렬 안정성:", stable([k.r for k in merge_sort([K(r) for r in recs])]))
    q = [K(r) for r in recs]; quick_sort(q)
    print("퀵 정렬 안정성:", stable([k.r for k in q]))
    sys.setrecursionlimit(10000)
    print("첫 원소 피벗, 정렬된 입력 500개의 재귀 깊이:", naive_quick_sort_depth(list(range(500))))
    print("첫 원소 피벗, 무작위 입력 500개의 재귀 깊이:", naive_quick_sort_depth([rng.random() for _ in range(500)]))
