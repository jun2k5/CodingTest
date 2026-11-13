"""기초 정렬: 버블, 선택, 삽입, 셸 정렬 (모두 제자리 정렬)."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


def bubble_sort(a):
    n = len(a)
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):          # 끝의 i개는 이미 자리를 잡았다
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
        if not swapped:                      # 한 바퀴 동안 교환이 없으면 정렬 완료
            break


def selection_sort(a):
    n = len(a)
    for i in range(n - 1):
        m = i
        for j in range(i + 1, n):
            if a[j] < a[m]:
                m = j
        a[i], a[m] = a[m], a[i]


def insertion_sort(a):
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:         # key보다 큰 원소를 한 칸씩 뒤로 민다
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key


def shell_sort(a):
    gap = len(a) // 2
    while gap > 0:
        for i in range(gap, len(a)):         # 간격이 gap인 원소들끼리 삽입 정렬
            key = a[i]
            j = i
            while j >= gap and a[j - gap] > key:
                a[j] = a[j - gap]
                j -= gap
            a[j] = key
        gap //= 2


def count_ops(fn, a):
    """비교 횟수를 세기 위해 원소를 감싼다."""
    cnt = [0]

    class C:
        __slots__ = ("v",)
        def __init__(self, v): self.v = v
        def __gt__(self, o): cnt[0] += 1; return self.v > o.v
        def __lt__(self, o): cnt[0] += 1; return self.v < o.v

    b = [C(x) for x in a]
    fn(b)
    return cnt[0]


if __name__ == "__main__":
    from _check import check_sort
    for f in (bubble_sort, selection_sort, insertion_sort, shell_sort):
        check_sort(f)
    import random
    rng = random.Random(1)
    n = 1000
    data = {"무작위": [rng.randint(0, 10**6) for _ in range(n)], "정렬됨": list(range(n)), "역순": list(range(n, 0, -1))}
    print(f"\n비교 횟수 (n={n})")
    print("알고리즘".ljust(10), *[k.rjust(9) for k in data])
    for f in (bubble_sort, selection_sort, insertion_sort, shell_sort):
        print(f.__name__.ljust(15), *[str(count_ops(f, v)).rjust(9) for v in data.values()])
    trace = [5, 2, 4, 6, 1, 3]
    print("\n삽입 정렬 추적", trace)
    a = trace[:]
    for i in range(1, len(a)):
        key = a[i]; j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]; j -= 1
        a[j + 1] = key
        print(f"  i={i} key={key} -> {a}")
