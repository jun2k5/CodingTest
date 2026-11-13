"""이분 매칭: 쿤(증가 경로 DFS) O(VE), 홉크로프트-카프 O(E√V), 헝가리안(가중치 할당 문제) O(n³)."""
import itertools, random
from collections import deque


def kuhn(n_left, n_right, adj):
    """왼쪽 정점마다 증가 경로를 찾는다. 이미 짝이 있는 오른쪽 정점은 그 짝이 다른 곳으로 옮길 수 있으면 빼앗는다."""
    match_r = [-1] * n_right
    def try_kuhn(v, seen):
        for u in adj[v]:
            if not seen[u]:
                seen[u] = True
                if match_r[u] == -1 or try_kuhn(match_r[u], seen):
                    match_r[u] = v
                    return True
        return False
    result = 0
    for v in range(n_left):
        if try_kuhn(v, [False] * n_right): result += 1
    return result, match_r


def hopcroft_karp(n_left, n_right, adj):
    """BFS로 짝 없는 왼쪽 정점들로부터 층을 나누고, 그 층을 따라 서로 겹치지 않는 최단 증가 경로를 DFS로 한꺼번에 찾는다."""
    INF = float("inf")
    ml, mr = [-1] * n_left, [-1] * n_right
    dist = [0] * n_left
    def bfs():
        q = deque()
        for v in range(n_left):
            if ml[v] == -1: dist[v] = 0; q.append(v)
            else: dist[v] = INF
        found = False
        while q:
            v = q.popleft()
            for u in adj[v]:
                w = mr[u]
                if w == -1: found = True
                elif dist[w] == INF:
                    dist[w] = dist[v] + 1; q.append(w)
        return found
    def dfs(v):
        for u in adj[v]:
            w = mr[u]
            if w == -1 or (dist[w] == dist[v] + 1 and dfs(w)):
                ml[v], mr[u] = u, v
                return True
        dist[v] = INF                              # 이번 단계에서 막힌 정점은 다시 보지 않는다
        return False
    result, phases = 0, 0
    while bfs():
        phases += 1
        for v in range(n_left):
            if ml[v] == -1 and dfs(v): result += 1
    return result, phases


def brute_matching(n_left, n_right, adj):
    edges = [(v, u) for v in range(n_left) for u in adj[v]]
    for k in range(min(n_left, n_right), 0, -1):
        for comb in itertools.combinations(edges, k):
            if len({v for v, _ in comb}) == k and len({u for _, u in comb}) == k:
                return k
    return 0


def hungarian(cost):
    """n x n 비용 행렬에서 각 행에 서로 다른 열을 하나씩 배정하는 최소 비용.
    퍼텐셜 u, v를 유지하며 cost[i][j] - u[i] - v[j] >= 0, 0인 간선(빡빡한 간선)으로만 증가 경로를 찾는다."""
    n = len(cost)
    INF = float("inf")
    u, v = [0] * (n + 1), [0] * (n + 1)
    p, way = [0] * (n + 1), [0] * (n + 1)          # p[j] = 열 j에 배정된 행 (1-indexed, 0은 가상)
    for i in range(1, n + 1):
        p[0] = i
        j0 = 0
        minv, used = [INF] * (n + 1), [False] * (n + 1)
        while True:
            used[j0] = True
            i0, delta, j1 = p[j0], INF, 0
            for j in range(1, n + 1):
                if not used[j]:
                    cur = cost[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j]: minv[j], way[j] = cur, j0
                    if minv[j] < delta: delta, j1 = minv[j], j
            for j in range(n + 1):                 # 퍼텐셜 조정: 새 빡빡한 간선을 하나 만든다
                if used[j]: u[p[j]] += delta; v[j] -= delta
                else: minv[j] -= delta
            j0 = j1
            if p[j0] == 0: break
        while j0:                                  # 증가 경로를 따라 배정을 뒤집는다
            j1 = way[j0]; p[j0] = p[j1]; j0 = j1
    assign = [0] * n
    for j in range(1, n + 1):
        if p[j]: assign[p[j] - 1] = j - 1
    return sum(cost[i][assign[i]] for i in range(n)), assign


if __name__ == "__main__":
    rng = random.Random(34)
    for _ in range(300):
        nl, nr = rng.randint(1, 6), rng.randint(1, 6)
        adj = [[u for u in range(nr) if rng.random() < 0.35] for _ in range(nl)]
        ref = brute_matching(nl, nr, adj)
        k, match_r = kuhn(nl, nr, adj)
        assert k == hopcroft_karp(nl, nr, adj)[0] == ref
        assert all(v in range(nl) and u in adj[v] for u, v in enumerate(match_r) if v != -1)
    print("쿤·홉크로프트-카프: 300개 이분 그래프에서 완전 탐색 최대 매칭과 일치")

    for _ in range(300):
        n = rng.randint(1, 7)
        cost = [[rng.randint(-5, 20) for _ in range(n)] for _ in range(n)]
        best = min(sum(cost[i][p[i]] for i in range(n)) for p in itertools.permutations(range(n)))
        c, a = hungarian(cost)
        assert c == best and sorted(a) == list(range(n))
    print("헝가리안: 300개 비용 행렬(음수 포함)에서 n! 완전 탐색 최소 비용과 일치")

    # 직원 5명, 일 5개: 직원별 할 수 있는 일
    adj = [[0, 1], [0], [1, 2, 3, 4], [1], [4]]
    k, mr = kuhn(5, 5, adj)
    print("이분 매칭 예제: 최대 매칭", k, "/ 일별 담당 직원", mr)

    cost = [[9, 2, 7, 8], [6, 4, 3, 7], [5, 8, 1, 8], [7, 6, 9, 4]]
    print("할당 문제 4x4 예제:", hungarian(cost))

    import time
    for n in (300, 1000):
        adj = [rng.sample(range(n), 5) for _ in range(n)]
        t0 = time.perf_counter(); a, _ = kuhn(n, n, adj); t1 = time.perf_counter()
        b, phases = hopcroft_karp(n, n, adj); t2 = time.perf_counter()
        assert a == b
        print(f"왼쪽·오른쪽 {n}개, 정점당 간선 5개: 최대 매칭 {a}, 쿤 {1000 * (t1 - t0):.0f}ms, "
              f"홉크로프트-카프 {1000 * (t2 - t1):.0f}ms (단계 {phases}번)")
