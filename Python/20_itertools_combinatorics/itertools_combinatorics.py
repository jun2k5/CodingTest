"""20. itertools ② 조합과 레시피: product, permutations, combinations, 공식 문서 레시피"""
import collections
import itertools as it
import math


def combinatorics():
    print("product('AB', repeat=2):", ["".join(p) for p in it.product("AB", repeat=2)])
    print("product(크기, 색):", list(it.product(["S", "M"], ["red", "blue"])))
    print("permutations('ABC', 2):", ["".join(p) for p in it.permutations("ABC", 2)])
    print("combinations('ABCD', 2):", ["".join(c) for c in it.combinations("ABCD", 2)])
    print("combinations_with_replacement('AB', 2):",
          ["".join(c) for c in it.combinations_with_replacement("AB", 2)])

    n, r = 10, 3
    counts = (len(list(it.permutations(range(n), r))), len(list(it.combinations(range(n), r))))
    print("개수 공식 확인 perm, comb:", counts, (math.perm(n, r), math.comb(n, r)))
    assert counts == (math.perm(n, r), math.comb(n, r))


def nested_loop_replacement():
    hits = [(x, y, z) for x, y, z in it.product(range(1, 20), repeat=3) if x <= y <= z and x * x + y * y == z * z]
    print("피타고라스 수(중첩 반복 대신 product):", hits)

    coins = [500, 100, 50]
    target = 1300
    ways = [combo for combo in it.product(range(4), repeat=len(coins))
            if sum(c * k for c, k in zip(coins, combo)) == target]
    print("동전 조합(개수 벡터):", ways)


def subset_sum():
    nums = [3, 34, 4, 12, 5, 2]
    target = 9
    found = [c for r in range(1, len(nums) + 1) for c in it.combinations(nums, r) if sum(c) == target]
    print("합이 9인 부분집합:", found)
    assert (4, 5) in found and (3, 4, 2) in found


# --- 공식 문서의 itertools 레시피(일부) ---
def take(n, iterable):
    return list(it.islice(iterable, n))


def nth(iterable, n, default=None):
    return next(it.islice(iterable, n, None), default)


def unique_everseen(iterable, key=None):
    seen = set()
    for element in iterable:
        k = element if key is None else key(element)
        if k not in seen:
            seen.add(k)
            yield element


def sliding_window(iterable, n):
    iterator = iter(iterable)
    window = collections.deque(it.islice(iterator, n - 1), maxlen=n)
    for x in iterator:
        window.append(x)
        yield tuple(window)


def partition(pred, iterable):
    t1, t2 = it.tee(iterable)
    return it.filterfalse(pred, t1), filter(pred, t2)


def roundrobin(*iterables):
    iterators = map(iter, iterables)
    for num_active in range(len(iterables), 0, -1):
        iterators = it.cycle(it.islice(iterators, num_active))
        yield from map(next, iterators)


def powerset(iterable):
    s = list(iterable)
    return it.chain.from_iterable(it.combinations(s, r) for r in range(len(s) + 1))


def recipes():
    print("take(3):", take(3, it.count(7)))
    print("nth(10번째):", nth(it.count(0, 2), 10))
    print("unique_everseen(순서 유지 중복 제거):", "".join(unique_everseen("AAAABBBCCDAABBB")))
    print("대소문자 무시:", list(unique_everseen(["a", "B", "A", "b", "c"], key=str.lower)))
    print("sliding_window(3):", list(sliding_window([1, 2, 3, 4, 5], 3)))
    evens_false, evens_true = partition(lambda x: x % 2 == 0, range(7))
    print("partition:", list(evens_false), list(evens_true))
    print("roundrobin:", "".join(roundrobin("ABC", "D", "EF")))
    print("powerset:", list(powerset("ab")))
    assert list(sliding_window([1, 2, 3, 4], 2)) == [(1, 2), (2, 3), (3, 4)]
    assert list(sliding_window(iter([1, 2, 3, 4]), 2)) == [(1, 2), (2, 3), (3, 4)]  # 이터레이터 입력


def explosion():
    for n in (5, 10, 15):
        print(f"permutations({n}) 개수: {math.factorial(n):,}")


if __name__ == "__main__":
    combinatorics()
    nested_loop_replacement()
    subset_sum()
    recipes()
    explosion()
    print("모든 검증 통과")
