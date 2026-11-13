"""음수 간선이 있는 최단 경로: 벨만-포드(음수 사이클 판정), 플로이드-워셜, 존슨."""
import heapq, random

INF = float("inf")


def bellman_ford(n, edges, s):
    """V-1번 모든 간선을 완화. V번째에도 줄어들면 s에서 도달 가능한 음수 사이클이 있다 → None."""
    dist = [INF] * n
    dist[s] = 0
    for i in range(n):
        changed = False
        for a, b, w in edges:
            if dist[a] != INF and dist[a] + w < dist[b]:
                dist[b] = dist[a] + w
                changed = True
                if i == n - 1: return None
        if not changed: break                     # 더 바뀌지 않으면 일찍 끝낸다
    return dist


def floyd_warshall(n, edges):
    """d[i][j]를 '중간 정점으로 0..k만 쓸 때'로 k를 늘려 가며 갱신. d[i][i] < 0이면 음수 사이클."""
    d = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    for a, b, w in edges:
        d[a][b] = min(d[a][b], w)
    for k in range(n):
        dk = d[k]
        for i in range(n):
            dik = d[i][k]
            if dik == INF: continue
            di = d[i]
            for j in range(n):
                if dik + dk[j] < di[j]:
                    di[j] = dik + dk[j]
    return d


def has_negative_cycle_fw(d):
    return any(d[i][i] < 0 for i in range(len(d)))


def johnson(n, edges):
    """가상 정점 q에서 벨만-포드로 h를 구해 w'(a,b) = w + h[a] - h[b] >= 0으로 바꾼 뒤
    정점마다 다익스트라. 희소 그래프의 전체 쌍 최단 경로 O(VE log V)."""
    h = bellman_ford(n + 1, edges + [(n, v, 0) for v in range(n)], n)
    if h is None: return None
    g = [[] for _ in range(n)]
    for a, b, w in edges:
        g[a].append((b, w + h[a] - h[b]))
    res = []
    for s in range(n):
        dist = [INF] * n; dist[s] = 0
        pq = [(0, s)]
        while pq:
            dd, v = heapq.heappop(pq)
            if dd > dist[v]: continue
            for u, w in g[v]:
                if dd + w < dist[u]:
                    dist[u] = dd + w; heapq.heappush(pq, (dist[u], u))
        res.append([dist[t] - h[s] + h[t] if dist[t] != INF else INF for t in range(n)])
    return res


def random_no_neg_cycle(rng, n, p):
    """퍼텐셜 trick: 음이 아닌 가중치 c에 pot[a] - pot[b]를 더하면 음수 간선은 생기지만 사이클 합은 c의 합 >= 0."""
    pot = [rng.randint(-20, 20) for _ in range(n)]
    return [(a, b, rng.randint(0, 10) + pot[a] - pot[b])
            for a in range(n) for b in range(n) if a != b and rng.random() < p]


def brute_shortest(n, edges, s):
    """검증용: 단순 경로(정점 중복 없음)를 모두 따라가 본다. 음수 사이클이 없으면 최단 경로는 단순 경로."""
    g = [[] for _ in range(n)]
    for a, b, w in edges: g[a].append((b, w))
    best = [INF] * n; best[s] = 0
    def go(v, cost, seen):
        for u, w in g[v]:
            if not seen >> u & 1:
                if cost + w < best[u]: best[u] = cost + w
                go(u, cost + w, seen | 1 << u)
    go(s, 0, 1 << s)
    return best


if __name__ == "__main__":
    rng = random.Random(29)
    for _ in range(300):
        n = rng.randint(1, 8)
        edges = random_no_neg_cycle(rng, n, 0.35)
        fw = floyd_warshall(n, edges)
        jo = johnson(n, edges)
        assert not has_negative_cycle_fw(fw)
        for s in range(n):
            ref = brute_shortest(n, edges, s)
            assert bellman_ford(n, edges, s) == ref == fw[s] == jo[s]
    print("벨만-포드·플로이드-워셜·존슨: 음수 간선 포함 300개 그래프에서 단순 경로 완전 탐색과 일치")

    # 음수 사이클 판정: 벨만-포드(모든 정점에서) vs 플로이드-워셜
    neg = 0
    for _ in range(500):
        n = rng.randint(1, 8)
        edges = [(a, b, rng.randint(-5, 10)) for a in range(n) for b in range(n) if a != b and rng.random() < 0.3]
        fw_neg = has_negative_cycle_fw(floyd_warshall(n, edges))
        bf_neg = any(bellman_ford(n, edges, s) is None for s in range(n))
        assert fw_neg == bf_neg == (johnson(n, edges) is None)
        neg += fw_neg
    print(f"음수 사이클 판정: 500개 그래프 중 {neg}개에서 세 방법 모두 사이클 검출, 나머지 모두 없음으로 일치")

    # 백준 11657 타임머신 예제 1, 2, 3 (1번부터 → 0번부터)
    ex1 = [(0, 1, 4), (0, 2, 3), (1, 2, -1), (2, 0, -2)]
    ex2 = [(0, 1, 4), (0, 2, 3), (1, 2, -4), (2, 0, -2)]
    ex3 = [(0, 1, 4), (1, 0, 3)]
    for name, n, e in (("예제 1", 3, ex1), ("예제 2", 3, ex2), ("예제 3", 3, ex3)):
        r = bellman_ford(n, e, 0)
        print(f"백준 11657 {name}:", "-1 (음수 사이클)" if r is None else [x if x != INF else -1 for x in r[1:]])

    # 플로이드-워셜 표 예제
    e = [(0, 1, 3), (1, 2, -2), (0, 2, 4), (2, 3, 2), (3, 0, 1)]
    for row in floyd_warshall(4, e):
        print("  ", row)
