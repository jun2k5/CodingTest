"""34. 성능 측정: perf_counter, timeit(repeat·min), cProfile·pstats, tracemalloc, 측정 주의점"""
import cProfile
import io
import pstats
import time
import timeit
import tracemalloc


def slow_unique(items):
    result = []
    for x in items:
        if x not in result:          # list in → O(n) → 전체 O(n²)
            result.append(x)
    return result


def fast_unique(items):
    return list(dict.fromkeys(items))   # 순서 유지 + O(n)


def parse(lines):
    return [int(s) for s in lines if s.isdigit()]


def pipeline(n):
    lines = [str(i % 500) for i in range(n)]
    nums = parse(lines)
    return slow_unique(nums)


def perf_counter_demo():
    start = time.perf_counter()
    sum(range(1_000_000))
    elapsed = time.perf_counter() - start
    print(f"perf_counter 1회 측정: {elapsed * 1000:.2f}ms")


def timeit_demo():
    data = list(range(2000)) * 2
    assert slow_unique(data) == fast_unique(data)
    slow = timeit.repeat(lambda: slow_unique(data), number=5, repeat=5)
    fast = timeit.repeat(lambda: fast_unique(data), number=5, repeat=5)
    print(f"slow_unique 최솟값: {min(slow) / 5 * 1000:.1f}ms/회 (5회 중 편차 {max(slow) / min(slow):.2f}배)")
    print(f"fast_unique 최솟값: {min(fast) / 5 * 1000:.3f}ms/회")
    t = timeit.Timer("x in s", setup="s = set(range(1000)); x = 999")
    number, total = t.autorange()
    print(f"autorange: {number}회 반복에 {total:.2f}s → 1회 {total / number * 1e9:.0f}ns")


def cprofile_demo():
    profiler = cProfile.Profile()
    profiler.enable()
    pipeline(20_000)
    profiler.disable()
    out = io.StringIO()
    stats = pstats.Stats(profiler, stream=out).sort_stats("cumulative")
    stats.print_stats(6)
    lines = [l for l in out.getvalue().splitlines() if "profiling.py" in l or "ncalls" in l]
    print("cProfile 상위(누적 시간순):")
    for l in lines[:5]:
        print("  " + " ".join(l.split()).replace(__file__, "profiling.py"))


def tracemalloc_demo():
    tracemalloc.start()
    big = [str(i) for i in range(100_000)]
    current, peak = tracemalloc.get_traced_memory()
    snapshot = tracemalloc.take_snapshot()
    tracemalloc.stop()
    top = snapshot.statistics("lineno")[0]
    print(f"tracemalloc 현재 {current / 1024 / 1024:.1f}MB, 최대 {peak / 1024 / 1024:.1f}MB, 최대 할당 줄: {top.traceback[0].lineno}행")
    del big


if __name__ == "__main__":
    perf_counter_demo()
    timeit_demo()
    cprofile_demo()
    tracemalloc_demo()
    print("모든 검증 통과")
