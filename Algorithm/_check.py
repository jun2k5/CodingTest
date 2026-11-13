"""정렬 함수 공통 검증 도구: 무작위 입력을 sorted()와 비교한다."""
import random


def check_sort(fn, trials=500, max_n=60, lo=-50, hi=50, inplace=True, name=None):
    rng = random.Random(42)
    cases = [[], [1], [2, 1], [1, 1, 1], list(range(10)), list(range(10, 0, -1))]
    for _ in range(trials):
        n = rng.randint(0, max_n)
        cases.append([rng.randint(lo, hi) for _ in range(n)])
    for a in cases:
        expected = sorted(a)
        b = a[:]
        out = fn(b)
        got = b if inplace and out is None else out
        assert got == expected, (name or fn.__name__, a, got)
    print(f"{name or fn.__name__}: {len(cases)}개 입력 통과")
