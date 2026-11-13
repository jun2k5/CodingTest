"""최소 신장 트리: 크루스칼(정렬 + 유니온 파인드), 프림(우선순위 큐), 보루프카."""
import heapq, itertools, random


class DSU:
    def __init__(self, n):
        self.p = list(range(n)); self.r = [0] * n

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a == b: return False
        if self.r[a] < self.r[b]: a, b = b, a
        self.p[b] = a
        if self.r[a] == self.r[b]: self.r[a] += 1
        return True


def kruskal(n, edges):
    """edges = [(w, a, b)]. 가벼운 간선부터 사이클을 만들지 않으면 넣는다."""
    d, total, used = DSU(n), 0, []
    for w, a, b in sorted(edges):
        if d.union(a, b):
            total += w; used.append((w, a, b))
            if len(used) == n - 1: break
    return (total, used) if len(used) == n - 1 else (None, used)


def prim(n, edges):
    """트리에 붙은 정점에서 나가는 가장 가벼운 간선을 하나씩 추가."""
    g = [[] for _ in range(n)]
    for w, a, b in edges:
        g[a].append((w, b)); g[b].append((w, a))
    seen = [False] * n
    pq, total, cnt = [(0, 0)], 0, 0
    while pq and cnt < n:
        w, v = heapq.heappop(pq)
        if seen[v]: continue
        seen[v] = True; total += w; cnt += 1
        for nw, u in g[v]:
            if not seen[u]: heapq.heappush(pq, (nw, u))
    return total if cnt == n else None


def prim_array(n, edges):
    """인접 행렬 + 선형 탐색. O(V^2)라 간선이 V^2에 가까운 밀집 그래프에서 유리."""
    INF = float("inf")
    w = [[INF] * n for _ in range(n)]
    for c, a, b in edges:
        if c < w[a][b]: w[a][b] = w[b][a] = c
    best, seen, total = [INF] * n, [False] * n, 0
    best[0] = 0
    for _ in range(n):
        v, bv = -1, INF
        for i in range(n):
            if not seen[i] and best[i] < bv: v, bv = i, best[i]
        if v == -1: return None
        seen[v] = True; total += bv
        wv = w[v]
        for u in range(n):
            if not seen[u] and wv[u] < best[u]: best[u] = wv[u]
    return total


def boruvka(n, edges):
    """모든 컴포넌트가 동시에 '밖으로 나가는 가장 가벼운 간선'을 고른다. 매 라운드 컴포넌트 수가 절반 이하.
    가중치가 같을 때 사이클을 막기 위해 (가중치, 간선 번호)로 비교한다."""
    d, total, comps = DSU(n), 0, n
    while comps > 1:
        cheapest = {}
        for idx, (w, a, b) in enumerate(edges):
            ra, rb = d.find(a), d.find(b)
            if ra == rb: continue
            key = (w, idx)
            for r in (ra, rb):
                if r not in cheapest or key < cheapest[r]: cheapest[r] = key
        if not cheapest: return None              # 더 연결할 간선이 없다 → 연결 그래프가 아님
        for w, idx in cheapest.values():
            _, a, b = edges[idx]
            if d.union(a, b):
                total += w; comps -= 1
    return total


def brute_mst(n, edges):
    best = None
    for comb in itertools.combinations(edges, n - 1):
        d = DSU(n)
        if all(d.union(a, b) for _, a, b in comb):
            s = sum(w for w, _, _ in comb)
            best = s if best is None else min(best, s)
    return best if n > 1 else 0


if __name__ == "__main__":
    rng = random.Random(31)
    for _ in range(300):
        n = rng.randint(1, 7)
        edges = [(rng.randint(1, 6), a, b) for a in range(n) for b in range(a + 1, n) if rng.random() < 0.6]
        ref = brute_mst(n, edges)
        k, used = kruskal(n, edges)
        assert k == prim(n, edges) == prim_array(n, edges) == boruvka(n, edges) == ref, (n, edges)
    print("크루스칼·프림·보루프카: 300개 그래프(같은 가중치 포함)에서 완전 탐색 최소 비용과 일치")

    # 백준 1197 예제 (1번부터 → 0번부터)
    e = [(1, 0, 1), (2, 1, 2), (3, 0, 2)]
    print("백준 1197 예제:", kruskal(3, e)[0], prim(3, e), boruvka(3, e))

    e = [(7, 0, 1), (5, 0, 3), (8, 1, 2), (9, 1, 3), (7, 1, 4), (5, 2, 4),
         (15, 3, 4), (6, 3, 5), (8, 4, 5), (9, 4, 6), (11, 5, 6)]
    total, used = kruskal(7, e)
    print("정점 7개 예제: 크루스칼", total, "선택 간선(가중치, a, b)", used)
    print("                 프림", prim(7, e), "/ 보루프카", boruvka(7, e))

    # 크루스칼 vs 프림 시간: 희소·밀집
    import time
    for n, m in ((5000, 15000), (1500, 1500 * 1499 // 2)):
        if m == n * (n - 1) // 2:
            edges = [(rng.randint(1, 10**6), a, b) for a in range(n) for b in range(a + 1, n)]
        else:
            edges = [(rng.randint(1, 10**6), i, i + 1) for i in range(n - 1)]
            edges += [(rng.randint(1, 10**6), rng.randrange(n), rng.randrange(n)) for _ in range(m - n + 1)]
        t0 = time.perf_counter(); a = kruskal(n, edges)[0]; t1 = time.perf_counter()
        b = prim(n, edges); t2 = time.perf_counter()
        c = prim_array(n, edges); t3 = time.perf_counter()
        assert a == b == c
        print(f"V={n:,}, E={len(edges):,}: 크루스칼 {1000 * (t1 - t0):.0f}ms, 프림(힙) {1000 * (t2 - t1):.0f}ms, 프림(배열) {1000 * (t3 - t2):.0f}ms")
