"""최적화 DP: 0-1 배낭(2차원·1차원 + 선택 복원), 행렬 곱셈 순서."""
import itertools, random


def knapsack_2d(items, cap):
    """items = [(무게, 가치)]. dp[i][w] = 앞 i개로 용량 w일 때 최대 가치. 선택한 물건도 복원."""
    n = len(items)
    dp = [[0] * (cap + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        wt, val = items[i - 1]
        for w in range(cap + 1):
            dp[i][w] = dp[i - 1][w]
            if wt <= w and dp[i - 1][w - wt] + val > dp[i][w]:
                dp[i][w] = dp[i - 1][w - wt] + val
    chosen, w = [], cap
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:              # 값이 달라졌으면 i번째를 넣은 것
            chosen.append(i - 1); w -= items[i - 1][0]
    return dp[n][cap], chosen[::-1]


def knapsack_1d(items, cap):
    """1차원 배열. 무게를 큰 쪽부터 돌아야 같은 물건을 두 번 넣지 않는다."""
    dp = [0] * (cap + 1)
    for wt, val in items:
        for w in range(cap, wt - 1, -1):
            dp[w] = max(dp[w], dp[w - wt] + val)
    return dp[cap]


def knapsack_unbounded(items, cap):
    """같은 물건을 여러 번 넣을 수 있으면 무게를 작은 쪽부터 돈다."""
    dp = [0] * (cap + 1)
    for wt, val in items:
        for w in range(wt, cap + 1):
            dp[w] = max(dp[w], dp[w - wt] + val)
    return dp[cap]


def matrix_chain(dims):
    """행렬 i의 크기 dims[i] x dims[i+1]. 곱셈 최소 횟수와 괄호 순서."""
    n = len(dims) - 1
    dp = [[0] * n for _ in range(n)]
    split = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):                # 짧은 구간부터
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = float("inf")
            for k in range(i, j):                 # 마지막 곱셈을 어디서 나눌지
                cost = dp[i][k] + dp[k + 1][j] + dims[i] * dims[k + 1] * dims[j + 1]
                if cost < dp[i][j]:
                    dp[i][j], split[i][j] = cost, k

    def paren(i, j):
        if i == j: return f"A{i + 1}"
        k = split[i][j]
        return f"({paren(i, k)}{paren(k + 1, j)})"
    return dp[0][n - 1], paren(0, n - 1)


def matrix_chain_brute(dims):
    def go(i, j):
        if i == j: return 0
        return min(go(i, k) + go(k + 1, j) + dims[i] * dims[k + 1] * dims[j + 1] for k in range(i, j))
    return go(0, len(dims) - 2)


if __name__ == "__main__":
    rng = random.Random(73)
    for _ in range(300):
        items = [(rng.randint(1, 10), rng.randint(1, 30)) for _ in range(rng.randint(0, 10))]
        cap = rng.randint(0, 30)
        brute = max(sum(items[i][1] for i in range(len(items)) if m >> i & 1)
                    for m in range(1 << len(items)) if sum(items[i][0] for i in range(len(items)) if m >> i & 1) <= cap)
        v2, chosen = knapsack_2d(items, cap)
        assert v2 == knapsack_1d(items, cap) == brute
        assert sum(items[i][0] for i in chosen) <= cap and sum(items[i][1] for i in chosen) == brute
    print("0-1 배낭(2차원·1차원·복원): 300개 입력에서 완전 탐색과 일치")
    items = [(6, 13), (4, 8), (3, 6), (5, 12)]
    print("백준 12865 예제 (무게, 가치) =", items, "용량 7 ->", knapsack_2d(items, 7))
    print("같은 물건 여러 번 허용하면 ->", knapsack_unbounded(items, 7))

    for _ in range(200):
        dims = [rng.randint(1, 20) for _ in range(rng.randint(2, 8))]
        assert matrix_chain(dims)[0] == matrix_chain_brute(dims)
    print("행렬 곱셈 순서: 200개 입력에서 모든 괄호 방식 완전 탐색과 일치")
    dims = [10, 30, 5, 60]
    print("A(10x30) B(30x5) C(5x60):", matrix_chain(dims), " 반대 순서 A(BC) 비용 =", 30 * 5 * 60 + 10 * 30 * 60)
