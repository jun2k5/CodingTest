"""다익스트라: 우선순위 큐 O((V+E) log V), 배열 O(V^2), 경로 복원, 음수 간선 반례."""
import heapq, random, time


def dijkstra(n, edges, s):
    """edges = [(a, b, w)] 방향 간선, w >= 0. (거리, 직전 정점) 반환."""
    g = [[] for _ in range(n)]
    for a, b, w in edges: g[a].append((b, w))
    INF = float("inf")
    dist, prev = [INF] * n, [-1] * n
    dist[s] = 0
    pq = [(0, s)]
    while pq:
        d, v = heapq.heappop(pq)
        if d > dist[v]: continue                  # 이미 더 짧은 거리로 확정된 낡은 항목
        for u, w in g[v]:
            nd = d + w
            if nd < dist[u]:
                dist[u], prev[u] = nd, v
                heapq.heappush(pq, (nd, u))
    return dist, prev


def dijkstra_array(n, edges, s):
    """힙 없이 매번 미확정 정점 중 최솟값을 선형 탐색. 간선이 매우 많을 때(V^2에 가까울 때) 유리."""
    INF = float("inf")
    w = [[INF] * n for _ in range(n)]
    for a, b, c in edges: w[a][b] = min(w[a][b], c)
    dist, done = [INF] * n, [False] * n
    dist[s] = 0
    for _ in range(n):
        v, best = -1, INF
        for i in range(n):
            if not done[i] and dist[i] < best: v, best = i, dist[i]
        if v == -1: break
        done[v] = True
        for u in range(n):
            if not done[u] and w[v][u] != INF and dist[v] + w[v][u] < dist[u]:
                dist[u] = dist[v] + w[v][u]
    return dist


def restore(prev, s, t):
    if t != s and prev[t] == -1: return None
    path = [t]
    while path[-1] != s: path.append(prev[path[-1]])
    return path[::-1]


def bellman_ford_ref(n, edges, s):
    INF = float("inf")
    dist = [INF] * n; dist[s] = 0
    for _ in range(n - 1):
        for a, b, w in edges:
            if dist[a] + w < dist[b]: dist[b] = dist[a] + w
    return dist


if __name__ == "__main__":
    rng = random.Random(28)
    for _ in range(400):
        n = rng.randint(1, 15)
        edges = [(a, b, rng.randint(0, 20)) for a in range(n) for b in range(n) if a != b and rng.random() < 0.3]
        s = rng.randrange(n)
        dist, prev = dijkstra(n, edges, s)
        assert dist == bellman_ford_ref(n, edges, s) == dijkstra_array(n, edges, s)
        wmap = {}
        for a, b, w in edges: wmap[(a, b)] = min(wmap.get((a, b), w), w)
        for t in range(n):
            p = restore(prev, s, t)
            assert (p is None) == (dist[t] == float("inf"))
            if p: assert sum(wmap[(a, b)] for a, b in zip(p, p[1:])) == dist[t]
    print("다익스트라(힙·배열), 경로 복원: 400개 그래프에서 벨만-포드와 일치")

    # 백준 1753 예제 (1번부터 → 0번부터)
    e = [(4, 0, 1), (0, 1, 2), (0, 2, 3), (1, 2, 4), (1, 3, 5), (2, 3, 6)]
    d, prev = dijkstra(5, e, 0)
    print("백준 1753 예제:", ["INF" if x == float("inf") else x for x in d])
    print("0 -> 3 경로:", restore(prev, 0, 3))

    # 음수 간선 반례: 0->1 (1), 0->2 (2), 2->1 (-2)
    e = [(0, 1, 1), (0, 2, 2), (2, 1, -2)]
    d_arr = dijkstra_array(3, e, 0)
    print("음수 간선 그래프 0→1 거리: 배열 다익스트라", d_arr[1], "/ 벨만-포드", bellman_ford_ref(3, e, 0)[1])

    # 힙 vs 배열 시간 비교
    for n, deg in ((2000, 5), (1000, 999)):
        edges = [(a, rng.randrange(n), rng.randint(1, 100)) for a in range(n) for _ in range(deg)]
        t0 = time.perf_counter(); dijkstra(n, edges, 0); t1 = time.perf_counter()
        dijkstra_array(n, edges, 0); t2 = time.perf_counter()
        print(f"V={n}, E={len(edges):,}: 힙 {1000 * (t1 - t0):.0f}ms, 배열 {1000 * (t2 - t1):.0f}ms")
