"""그래프 표현과 탐색: 인접 행렬/리스트, BFS, DFS(재귀·반복), 0-1 BFS, 양방향 BFS, IDDFS."""
import heapq, random
from collections import deque


def to_matrix(n, edges, directed=False):
    m = [[0] * n for _ in range(n)]
    for a, b in edges:
        m[a][b] = 1
        if not directed: m[b][a] = 1
    return m


def to_list(n, edges, directed=False):
    g = [[] for _ in range(n)]
    for a, b in edges:
        g[a].append(b)
        if not directed: g[b].append(a)
    return g


def bfs(g, s):
    """가중치 없는 그래프에서 s로부터의 최단 거리(간선 수). 도달 불가는 -1."""
    dist = [-1] * len(g)
    dist[s] = 0
    q = deque([s])
    while q:
        v = q.popleft()
        for u in g[v]:
            if dist[u] == -1:
                dist[u] = dist[v] + 1
                q.append(u)
    return dist


def bfs_path(g, s, t):
    """최단 경로 자체를 복원한다."""
    prev = [-1] * len(g)
    seen = [False] * len(g); seen[s] = True
    q = deque([s])
    while q:
        v = q.popleft()
        if v == t: break
        for u in g[v]:
            if not seen[u]:
                seen[u] = True; prev[u] = v; q.append(u)
    if not seen[t]: return None
    path = [t]
    while path[-1] != s: path.append(prev[path[-1]])
    return path[::-1]


def dfs_recursive(g, s, seen=None, order=None):
    if seen is None: seen, order = [False] * len(g), []
    seen[s] = True; order.append(s)
    for u in g[s]:
        if not seen[u]:
            dfs_recursive(g, u, seen, order)
    return order


def dfs_iterative(g, s):
    """재귀와 같은 방문 순서를 내기 위해 이웃을 거꾸로 넣고, 꺼낼 때 방문 처리한다."""
    seen, order, stack = [False] * len(g), [], [s]
    while stack:
        v = stack.pop()
        if seen[v]: continue
        seen[v] = True; order.append(v)
        for u in reversed(g[v]):
            if not seen[u]: stack.append(u)
    return order


def count_components(g):
    seen, comp = [False] * len(g), 0
    for v in range(len(g)):
        if not seen[v]:
            comp += 1
            for u in dfs_iterative(g, v): seen[u] = True
    return comp


def zero_one_bfs(n, wedges, s):
    """간선 가중치가 0 또는 1. 0이면 덱 앞, 1이면 덱 뒤에 넣는다."""
    g = [[] for _ in range(n)]
    for a, b, w in wedges: g[a].append((b, w))
    INF = float("inf")
    dist = [INF] * n; dist[s] = 0
    dq = deque([s])
    while dq:
        v = dq.popleft()
        for u, w in g[v]:
            if dist[v] + w < dist[u]:
                dist[u] = dist[v] + w
                if w == 0: dq.appendleft(u)
                else: dq.append(u)
    return dist


def dijkstra_ref(n, wedges, s):
    g = [[] for _ in range(n)]
    for a, b, w in wedges: g[a].append((b, w))
    INF = float("inf")
    dist = [INF] * n; dist[s] = 0
    pq = [(0, s)]
    while pq:
        d, v = heapq.heappop(pq)
        if d > dist[v]: continue
        for u, w in g[v]:
            if d + w < dist[u]:
                dist[u] = d + w; heapq.heappush(pq, (dist[u], u))
    return dist


def bidirectional_bfs(g, s, t):
    """s와 t 양쪽에서 한 층씩 번갈아(작은 쪽 먼저) 넓힌다. (거리, 방문 정점 수) 반환. 무방향 그래프."""
    if s == t: return 0, 1
    ds, dt = {s: 0}, {t: 0}
    qs, qt = deque([s]), deque([t])
    visited = 2
    while qs and qt:
        if len(qs) <= len(qt): q, mine, other = qs, ds, dt
        else: q, mine, other = qt, dt, ds
        best = None
        for _ in range(len(q)):                   # 한 층 전체를 처리
            v = q.popleft()
            for u in g[v]:
                if u in other:
                    cand = mine[v] + 1 + other[u]
                    best = cand if best is None else min(best, cand)
                if u not in mine:
                    mine[u] = mine[v] + 1; q.append(u); visited += 1
        if best is not None:
            return best, visited
    return -1, visited


def iddfs(g, s, t, max_depth):
    """깊이 제한 DFS를 제한 0, 1, 2, ...로 늘려 가며 반복. 처음 찾은 깊이가 최단 거리."""
    def dls(v, depth, on_path):
        if v == t: return True
        if depth == 0: return False
        for u in g[v]:
            if u not in on_path:
                on_path.add(u)
                if dls(u, depth - 1, on_path): return True
                on_path.discard(u)
        return False
    for limit in range(max_depth + 1):
        if dls(s, limit, {s}): return limit
    return -1


def random_graph(rng, n, p):
    return [(a, b) for a in range(n) for b in range(a + 1, n) if rng.random() < p]


if __name__ == "__main__":
    rng = random.Random(26)

    # 표현 두 가지가 같은 그래프인지
    for _ in range(200):
        n = rng.randint(1, 12)
        e = random_graph(rng, n, 0.3)
        m, g = to_matrix(n, e), to_list(n, e)
        assert all((m[a][b] == 1) == (b in g[a]) for a in range(n) for b in range(n))

    # BFS 거리 = 모든 간선 가중치 1인 다익스트라, 경로 길이 = 거리
    # 재귀 DFS와 반복 DFS의 방문 순서 동일
    for _ in range(300):
        n = rng.randint(1, 15)
        e = random_graph(rng, n, rng.random() * 0.5)
        g = to_list(n, e)
        s, t = rng.randrange(n), rng.randrange(n)
        ref = dijkstra_ref(n, [(a, b, 1) for a, b in e] + [(b, a, 1) for a, b in e], s)
        dist = bfs(g, s)
        assert dist == [-1 if x == float("inf") else x for x in ref]
        p = bfs_path(g, s, t)
        assert (p is None) == (dist[t] == -1)
        if p:
            assert len(p) - 1 == dist[t] and all(b in g[a] for a, b in zip(p, p[1:]))
        assert dfs_recursive(g, s) == dfs_iterative(g, s)
        assert sorted(dfs_iterative(g, s)) == [v for v in range(n) if dist[v] != -1]
    print("BFS 거리·경로, 재귀/반복 DFS 순서: 300개 그래프에서 검증 통과")

    # 0-1 BFS = 다익스트라
    for _ in range(300):
        n = rng.randint(1, 15)
        we = [(a, b, rng.randint(0, 1)) for a in range(n) for b in range(n) if a != b and rng.random() < 0.3]
        s = rng.randrange(n)
        assert zero_one_bfs(n, we, s) == dijkstra_ref(n, we, s)
    print("0-1 BFS: 300개 그래프에서 다익스트라와 일치")

    # 양방향 BFS와 IDDFS 거리 = BFS 거리
    for _ in range(300):
        n = rng.randint(1, 12)
        g = to_list(n, random_graph(rng, n, rng.random() * 0.5))
        s, t = rng.randrange(n), rng.randrange(n)
        d = bfs(g, s)[t]
        assert bidirectional_bfs(g, s, t)[0] == d
        assert iddfs(g, s, t, n) == d
    print("양방향 BFS, IDDFS: 300개 그래프에서 BFS 최단 거리와 일치")

    # 예제: 연결 요소
    g = to_list(6, [(0, 1), (0, 2), (3, 4)])
    print("정점 6개, 간선 (0,1)(0,2)(3,4): BFS 거리", bfs(g, 0), "/ 연결 요소", count_components(g), "개")
    g = to_list(7, [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)])
    print("트리 예제 BFS 순서 거리:", bfs(g, 0), " DFS 순서:", dfs_iterative(g, 0))

    # 양방향 BFS 방문 정점 수 비교: 격자 그래프에서 먼 두 점
    for size in (50, 200):
        n = size * size
        g = [[] for _ in range(n)]
        for r in range(size):
            for c in range(size):
                v = r * size + c
                if c + 1 < size: g[v].append(v + 1); g[v + 1].append(v)
                if r + 1 < size: g[v].append(v + size); g[v + size].append(v)
        s, t = (size // 2) * size + size // 4, (size // 2) * size + 3 * size // 4   # 같은 행, 거리 size/2
        dist = bfs(g, s)
        one_way = sum(1 for x in dist if x != -1 and x <= dist[t])
        d, vis = bidirectional_bfs(g, s, t)
        print(f"{size}x{size} 격자, 거리 {d}: 단방향 BFS가 연 정점 약 {one_way:,}개, 양방향 BFS {vis:,}개")
