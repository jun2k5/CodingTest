"""입력 크기에 따른 연산 횟수 증가와 실제 실행 시간."""
import math, sys, time


def ops_table():
    print("n".rjust(9), "log n".rjust(7), "n log n".rjust(12), "n^2".rjust(16), "2^n".rjust(12))
    for n in [10, 100, 1_000, 10_000, 100_000, 1_000_000]:
        two = f"{2**n:.2e}" if n <= 1000 else "-"
        print(str(n).rjust(9), f"{math.log2(n):7.1f}", f"{n * math.log2(n):12.0f}", f"{n * n:16d}", two.rjust(12))


def timed(fn, n):
    t = time.perf_counter(); fn(n); return time.perf_counter() - t


def linear(n):
    s = 0
    for i in range(n): s += i
    return s


def quadratic(n):
    s = 0
    for i in range(n):
        for j in range(n): s += 1
    return s


if __name__ == "__main__":
    ops_table()
    print("\n실제 시간 (Python)")
    for n in [1_000, 2_000, 4_000]:
        print(f"n={n:5d}  O(n) {timed(linear, n) * 1000:7.3f}ms   O(n^2) {timed(quadratic, n) * 1000:9.1f}ms")
    a, last, grows = [], sys.getsizeof([]), []
    for i in range(64):
        a.append(i)
        s = sys.getsizeof(a)
        if s != last: grows.append(len(a)); last = s
    print("\nlist.append에서 메모리를 다시 잡은 시점(원소 수):", grows)
