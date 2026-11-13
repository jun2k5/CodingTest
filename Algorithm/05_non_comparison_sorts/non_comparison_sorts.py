"""계수 정렬, 기수 정렬(LSD), 버킷 정렬, 그리고 내장 정렬(Timsort) 비교."""
import sys, pathlib, random, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


def counting_sort(a, max_value=None):
    """0 이상 정수. O(n + k), k = 최댓값. 누적 합을 써서 안정 정렬로 만든다."""
    if not a: return []
    k = max(a) if max_value is None else max_value
    cnt = [0] * (k + 1)
    for x in a: cnt[x] += 1
    for v in range(1, k + 1): cnt[v] += cnt[v - 1]   # cnt[v] = v 이하 원소 수
    out = [0] * len(a)
    for x in reversed(a):                              # 뒤에서부터 넣어야 안정적
        cnt[x] -= 1
        out[cnt[x]] = x
    return out


def radix_sort(a, base=10):
    """0 이상 정수, 낮은 자리부터(LSD). 자리마다 안정 정렬을 쓴다. O(d·(n + base))."""
    if not a: return []
    out, exp, m = a[:], 1, max(a)
    while m // exp > 0:
        buckets = [[] for _ in range(base)]
        for x in out: buckets[(x // exp) % base].append(x)
        out = [x for b in buckets for x in b]
        exp *= base
    return out


def bucket_sort(a, n_buckets=None):
    """[0, 1) 실수. 균등 분포면 평균 O(n)."""
    if not a: return []
    n = n_buckets or len(a)
    buckets = [[] for _ in range(n)]
    for x in a: buckets[min(int(x * n), n - 1)].append(x)
    out = []
    for b in buckets:
        b.sort()                       # 버킷 하나는 작으므로 어떤 정렬을 써도 된다
        out.extend(b)
    return out


if __name__ == "__main__":
    from _check import check_sort
    check_sort(counting_sort, inplace=False, lo=0, hi=100)
    check_sort(radix_sort, inplace=False, lo=0, hi=10**6)
    rng = random.Random(5)
    for _ in range(300):
        a = [rng.random() for _ in range(rng.randint(0, 80))]
        assert bucket_sort(a) == sorted(a)
    print("bucket_sort: 300개 입력 통과")

    print("\n기수 정렬 추적 [170, 45, 75, 90, 802, 24, 2, 66]")
    a, exp = [170, 45, 75, 90, 802, 24, 2, 66], 1
    while max(a) // exp > 0:
        bk = [[] for _ in range(10)]
        for x in a: bk[(x // exp) % 10].append(x)
        a = [x for b in bk for x in b]
        print(f"  {exp}의 자리 기준 -> {a}")
        exp *= 10

    n = 200_000
    data = [rng.randint(0, 999) for _ in range(n)]
    print()
    for name, f in [("counting_sort", lambda d: counting_sort(d, 999)), ("radix_sort", radix_sort), ("sorted (Timsort)", sorted)]:
        t = time.perf_counter(); f(data)
        print(f"{name:18s} n={n}: {time.perf_counter() - t:.3f}초")
    nearly = list(range(n))
    for _ in range(100):
        i, j = rng.randrange(n), rng.randrange(n)
        nearly[i], nearly[j] = nearly[j], nearly[i]
    rnd = [rng.random() for _ in range(n)]
    for name, d in [("거의 정렬된 입력", nearly), ("무작위 입력", rnd)]:
        t = time.perf_counter(); sorted(d)
        print(f"sorted {name}: {time.perf_counter() - t:.3f}초")
