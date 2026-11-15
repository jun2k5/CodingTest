"""21. functools ① 캐시: lru_cache, cache, 캐시 키 규칙, cache_info·cache_clear, cached_property"""
import functools
import time


def fib_plain(n):
    return n if n < 2 else fib_plain(n - 1) + fib_plain(n - 2)


@functools.cache                     # = lru_cache(maxsize=None), 3.9+
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)


def memoization():
    start = time.perf_counter()
    fib_plain(27)
    plain = time.perf_counter() - start
    start = time.perf_counter()
    fib(27)
    cached = time.perf_counter() - start
    print(f"fib(27) 캐시 없음: {plain * 1000:.0f}ms, 캐시: {cached * 1000:.3f}ms")
    print("fib(200):", fib(200))
    print("cache_info:", fib.cache_info())
    assert plain > cached


calls = []


@functools.lru_cache(maxsize=2)
def square(x):
    calls.append(x)
    return x * x


def lru_eviction():
    for x in [1, 2, 1, 3, 2]:
        square(x)
    print("실제 계산한 인자:", calls, "|", square.cache_info())
    assert calls == [1, 2, 3, 2]       # 3이 들어오며 가장 오래 안 쓴 2가 밀려남


@functools.lru_cache(maxsize=None)
def describe(x):
    return f"{type(x).__name__}:{x}"


@functools.lru_cache(maxsize=None, typed=True)
def describe_typed(x):
    return f"{type(x).__name__}:{x}"


def cache_keys():
    @functools.lru_cache(maxsize=None)
    def pair(a, b):
        return f"{type(a).__name__}:{a},{b}"
    print("typed=False, 인자 2개:", pair(1, "x"), pair(1.0, "x"), "| 1 == 1.0이라 같은 키")
    assert pair(1.0, "x") == "int:1,x"
    print("typed=False, 인자 1개:", describe(1), describe(1.0), "| int 단일 인자는 별도 키(구현 세부)")
    print("typed=True :", describe_typed(1), describe_typed(1.0))

    counter = []

    @functools.cache
    def f(a, b=0):
        counter.append((a, b))
        return a + b
    f(1, 2); f(1, b=2); f(a=1, b=2)
    print("인자 형태가 다르면 다른 키:", len(counter), "번 계산")
    assert len(counter) == 3

    try:
        describe([1, 2])
    except TypeError as e:
        print("해시 불가 인자:", e)


def mutable_return_trap():
    @functools.cache
    def default_tags():
        return ["new"]
    tags = default_tags()
    tags.append("sale")                # 캐시에 든 리스트 자체를 바꿈
    print("다음 호출 결과가 오염됨:", default_tags())
    assert default_tags() == ["new", "sale"]


class Report:
    def __init__(self, rows):
        self.rows = rows
        self.computed = 0

    @functools.cached_property
    def summary(self):
        self.computed += 1
        return {"count": len(self.rows), "total": sum(self.rows)}


def cached_property_demo():
    r = Report([3, 4, 5])
    print("cached_property:", r.summary, r.summary, "| 계산 횟수:", r.computed)
    print("인스턴스 __dict__에 저장:", "summary" in vars(r))
    del r.summary                      # 무효화
    r.rows.append(10)
    print("del 후 재계산:", r.summary, "| 계산 횟수:", r.computed)
    assert r.computed == 2


def clear():
    fib.cache_clear()
    print("cache_clear 후:", fib.cache_info())


if __name__ == "__main__":
    memoization()
    lru_eviction()
    cache_keys()
    mutable_return_trap()
    cached_property_demo()
    clear()
    print("모든 검증 통과")
