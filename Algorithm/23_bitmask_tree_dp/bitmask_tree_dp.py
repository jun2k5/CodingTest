"""비트마스크 DP(외판원 문제, Held-Karp)와 트리 DP(최대 독립 집합, 서브트리 크기)."""
import itertools, math, random, sys


def tsp_held_karp(d):
    """dp[mask][i] = 0에서 출발해 mask 도시를 방문하고 i에서 끝나는 최소 비용. O(n^2 2^n)."""
    n = len(d)
    INF = float("inf")
    dp = [[INF] * n for _ in range(1 << n)]
    dp[1][0] = 0
    for mask in range(1 << n):
        if not mask & 1: continue                 # 항상 0번 도시에서 출발
        for i in range(n):
            cur = dp[mask][i]
            if cur == INF or not mask >> i & 1: continue
            for j in range(n):
                if mask >> j & 1: continue
                nm = mask | 1 << j
                if cur + d[i][j] < dp[nm][j]:
                    dp[nm][j] = cur + d[i][j]
    full = (1 << n) - 1
    return min(dp[full][i] + d[i][0] for i in range(n)) if n > 1 else 0


def tsp_brute(d):
    n = len(d)
    if n == 1: return 0
    return min(sum(d[a][b] for a, b in zip((0,) + p, p + (0,))) for p in itertools.permutations(range(1, n)))


def tree_max_independent_set(n, edges, weight):
    """서로 인접하지 않은 정점들의 가중치 합 최대.
    dp[v][0] = v를 고르지 않을 때, dp[v][1] = v를 고를 때 (서브트리 기준)."""
    g = [[] for _ in range(n)]
    for a, b in edges:
        g[a].append(b); g[b].append(a)
    order, parent, stack = [], [-1] * n, [0]
    seen = [False] * n; seen[0] = True
    while stack:                                  # 반복 DFS로 방문 순서를 얻고 거꾸로 처리(자식 먼저)
        v = stack.pop(); order.append(v)
        for u in g[v]:
            if not seen[u]: seen[u] = True; parent[u] = v; stack.append(u)
    dp = [[0, w] for w in weight]
    size = [1] * n
    for v in reversed(order):
        p = parent[v]
        if p != -1:
            dp[p][0] += max(dp[v])                # 부모를 안 고르면 자식은 자유
            dp[p][1] += dp[v][0]                  # 부모를 고르면 자식은 못 고른다
            size[p] += size[v]
    return max(dp[0]), size


def mis_brute(n, edges, weight):
    best = 0
    for m in range(1 << n):
        if all(not (m >> a & 1 and m >> b & 1) for a, b in edges):
            best = max(best, sum(weight[i] for i in range(n) if m >> i & 1))
    return best


if __name__ == "__main__":
    rng = random.Random(79)
    for _ in range(100):
        n = rng.randint(1, 8)
        d = [[0 if i == j else rng.randint(1, 50) for j in range(n)] for i in range(n)]
        assert tsp_held_karp(d) == tsp_brute(d)
    print("외판원(비트마스크 DP): 100개 입력에서 순열 완전 탐색과 일치")
    for n in (10, 16, 20):
        print(f"도시 {n}개: 순열 {math.factorial(n - 1):,}가지, 비트마스크 DP 상태 {n * 2**n:,}개")

    for _ in range(300):
        n = rng.randint(1, 14)
        edges = [(i, rng.randrange(i)) for i in range(1, n)]
        w = [rng.randint(1, 20) for _ in range(n)]
        best, size = tree_max_independent_set(n, edges, w)
        assert best == mis_brute(n, edges, w) and size[0] == n
    print("트리 최대 독립 집합: 300개 무작위 트리에서 완전 탐색과 일치")
    edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5)]
    w = [10, 1, 1, 10, 10, 10]
    print("예제 트리 가중치", w, "->", tree_max_independent_set(6, edges, w)[0], "(0, 3, 4, 5 선택)")
