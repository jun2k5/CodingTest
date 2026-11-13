"""DP 기초: 피보나치(재귀·메모·표), 계단 오르기, 동전 교환(최소 개수·경우의 수)."""
import functools, itertools, random, sys, time

CALLS = [0]


def fib_naive(n):
    CALLS[0] += 1
    return n if n < 2 else fib_naive(n - 1) + fib_naive(n - 2)


@functools.lru_cache(maxsize=None)
def fib_memo(n):
    """하향식(top-down): 재귀 + 계산한 값 저장."""
    return n if n < 2 else fib_memo(n - 1) + fib_memo(n - 2)


def fib_table(n):
    """상향식(bottom-up): 작은 문제부터 표를 채운다. 직전 두 값만 있으면 되므로 O(1) 공간."""
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def climb_stairs(n, steps=(1, 2)):
    """n칸을 steps 크기로 오르는 방법 수. dp[i] = Σ dp[i - s]."""
    dp = [1] + [0] * n
    for i in range(1, n + 1):
        dp[i] = sum(dp[i - s] for s in steps if i >= s)
    return dp[n]


def coin_min(coins, amount):
    """금액을 만드는 최소 동전 수. 불가능하면 -1. dp[x] = min(dp[x - c] + 1)."""
    INF = float("inf")
    dp = [0] + [INF] * amount
    for x in range(1, amount + 1):
        for c in coins:
            if c <= x and dp[x - c] + 1 < dp[x]:
                dp[x] = dp[x - c] + 1
    return dp[amount] if dp[amount] != INF else -1


def coin_ways(coins, amount):
    """금액을 만드는 조합 수(순서 무관). 동전을 바깥 반복문에 두어야 순서가 다른 같은 조합을 한 번만 센다."""
    dp = [1] + [0] * amount
    for c in coins:
        for x in range(c, amount + 1):
            dp[x] += dp[x - c]
    return dp[amount]


def coin_ways_ordered(coins, amount):
    """순서까지 구분하는 경우의 수(1+2와 2+1을 다르게). 금액을 바깥에 둔다."""
    dp = [1] + [0] * amount
    for x in range(1, amount + 1):
        for c in coins:
            if c <= x:
                dp[x] += dp[x - c]
    return dp[amount]


if __name__ == "__main__":
    for n in range(25):
        assert fib_naive(n) == fib_memo(n) == fib_table(n)
    for n in (20, 25, 30):
        CALLS[0] = 0
        t = time.perf_counter(); fib_naive(n); dt = time.perf_counter() - t
        print(f"fib({n}) 단순 재귀: 호출 {CALLS[0]:,}번, {dt*1000:.0f}ms")
    t = time.perf_counter(); fib_table(10_000); print(f"fib(10000) 표 방식: {(time.perf_counter()-t)*1000:.2f}ms, {len(str(fib_table(10_000)))}자리")
    sys.setrecursionlimit(5000)
    print("fib_memo(1000) 앞 20자리:", str(fib_memo(1000))[:20])

    rng = random.Random(67)
    for _ in range(300):
        coins = sorted(set(rng.randint(1, 15) for _ in range(rng.randint(1, 4))))
        amount = rng.randint(0, 40)
        best, ways = -1, 0
        maxc = [amount // c for c in coins]
        for counts in itertools.product(*[range(m + 1) for m in maxc]):
            if sum(k * c for k, c in zip(counts, coins)) == amount:
                ways += 1
                s = sum(counts)
                best = s if best == -1 else min(best, s)
        assert coin_min(coins, amount) == best and coin_ways(coins, amount) == ways
    print("동전 교환(최소 개수·조합 수): 300개 입력에서 완전 탐색과 일치")
    print("계단 10칸(1·2칸):", climb_stairs(10), " = fib(11) =", fib_table(11))
    print("동전 [1,2,5]로 5원: 조합", coin_ways([1, 2, 5], 5), "가지, 순서 구분", coin_ways_ordered([1, 2, 5], 5), "가지")
    print("동전 [1,3,4]로 6원 최소 개수:", coin_min([1, 3, 4], 6), "(3+3)")
