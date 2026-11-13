"""연결성: 강한 연결 요소(코사라주·타잔), 단절점·단절선, 오일러 경로(히어홀저)."""
import random, sys
from collections import defaultdict

sys.setrecursionlimit(10000)


def kosaraju(n, edges):
    """1) 원래 그래프 DFS 종료 순서 기록 2) 역방향 그래프에서 종료 늦은 순으로 DFS → 한 번에 닿는 것이 SCC."""
    g = [[] for _ in range(n)]; rg = [[] for _ in range(n)]
    for a, b in edges: g[a].append(b); rg[b].append(a)
    seen, order = [False] * n, []
    def dfs1(v):
        seen[v] = True
        for u in g[v]:
            if not seen[u]: dfs1(u)
        order.append(v)
    for v in range(n):
        if not seen[v]: dfs1(v)
    comp = [-1] * n
    def dfs2(v, c):
        comp[v] = c
        for u in rg[v]:
            if comp[u] == -1: dfs2(u, c)
    c = 0
    for v in reversed(order):
        if comp[v] == -1: dfs2(v, c); c += 1
    return c, comp


def tarjan_scc(n, edges):
    """DFS 한 번. low[v] = v의 서브트리에서 스택에 남은 정점으로 갈 수 있는 가장 작은 방문 번호.
    low[v] == num[v]이면 v가 SCC의 루트 → 스택에서 v까지 꺼낸다."""
    g = [[] for _ in range(n)]
    for a, b in edges: g[a].append(b)
    num, low, on = [-1] * n, [0] * n, [False] * n
    stack, comp, cnt, c = [], [-1] * n, 0, 0
    def dfs(v):
        nonlocal cnt, c
        num[v] = low[v] = cnt; cnt += 1
        stack.append(v); on[v] = True
        for u in g[v]:
            if num[u] == -1:
                dfs(u); low[v] = min(low[v], low[u])
            elif on[u]:
                low[v] = min(low[v], num[u])
        if low[v] == num[v]:
            while True:
                u = stack.pop(); on[u] = False; comp[u] = c
                if u == v: break
            c += 1
    for v in range(n):
        if num[v] == -1: dfs(v)
    return c, comp


def scc_brute(n, edges):
    reach = [[i == j for j in range(n)] for i in range(n)]
    for a, b in edges: reach[a][b] = True
    for k in range(n):
        for i in range(n):
            if reach[i][k]:
                for j in range(n):
                    if reach[k][j]: reach[i][j] = True
    return {frozenset(j for j in range(n) if reach[i][j] and reach[j][i]) for i in range(n)}


def groups(comp):
    d = defaultdict(set)
    for v, c in enumerate(comp): d[c].add(v)
    return {frozenset(s) for s in d.values()}


def cut_vertices_and_bridges(n, edges):
    """무방향 그래프. low[u] >= num[v]인 자식 u가 있으면 v는 단절점(루트는 자식 2개 이상일 때),
    low[u] > num[v]이면 간선 (v, u)는 단절선. 다중 간선을 위해 간선 번호로 부모 간선을 구분한다."""
    g = [[] for _ in range(n)]
    for i, (a, b) in enumerate(edges):
        g[a].append((b, i)); g[b].append((a, i))
    num, low = [-1] * n, [0] * n
    cut, bridges, cnt = set(), [], 0
    def dfs(v, parent_edge):
        nonlocal cnt
        num[v] = low[v] = cnt; cnt += 1
        children = 0
        for u, ei in g[v]:
            if ei == parent_edge: continue
            if num[u] == -1:
                children += 1
                dfs(u, ei)
                low[v] = min(low[v], low[u])
                if parent_edge != -1 and low[u] >= num[v]: cut.add(v)
                if low[u] > num[v]: bridges.append(tuple(sorted((v, u))))
            else:
                low[v] = min(low[v], num[u])
        if parent_edge == -1 and children >= 2: cut.add(v)
    for v in range(n):
        if num[v] == -1: dfs(v, -1)
    return cut, sorted(bridges)


def n_components(n, edges, skip_vertex=-1, skip_edge=-1):
    p = list(range(n))
    def f(x):
        while p[x] != x: p[x] = p[p[x]]; x = p[x]
        return x
    for i, (a, b) in enumerate(edges):
        if i == skip_edge or skip_vertex in (a, b): continue
        p[f(a)] = f(b)
    return len({f(v) for v in range(n) if v != skip_vertex})


def euler_path(n, edges):
    """무방향 그래프 오일러 경로(모든 간선을 한 번씩). 홀수 차수 정점이 0개 또는 2개이고 간선이 한 덩어리여야 한다.
    히어홀저: 막힐 때까지 걷고, 막히면 되돌아오며 경로에 넣는다. O(E)."""
    g = [[] for _ in range(n)]
    for i, (a, b) in enumerate(edges):
        g[a].append((b, i)); g[b].append((a, i))
    odd = [v for v in range(n) if len(g[v]) % 2]
    if len(odd) not in (0, 2): return None
    start = odd[0] if odd else next((v for v in range(n) if g[v]), 0)
    used, ptr = [False] * len(edges), [0] * n
    stack, path = [start], []
    while stack:
        v = stack[-1]
        while ptr[v] < len(g[v]) and used[g[v][ptr[v]][1]]: ptr[v] += 1
        if ptr[v] == len(g[v]):
            path.append(stack.pop())
        else:
            u, ei = g[v][ptr[v]]
            used[ei] = True
            stack.append(u)
    if len(path) != len(edges) + 1: return None   # 간선이 여러 덩어리
    return path[::-1]


def euler_brute(n, edges):
    m = len(edges)
    def go(v, used):
        if used == (1 << m) - 1: return True
        for i, (a, b) in enumerate(edges):
            if not used >> i & 1 and v in (a, b):
                if go(b if v == a else a, used | 1 << i): return True
        return False
    return m == 0 or any(go(v, 0) for v in range(n))


if __name__ == "__main__":
    rng = random.Random(32)
    for _ in range(400):
        n = rng.randint(1, 10)
        edges = [(a, b) for a in range(n) for b in range(n) if a != b and rng.random() < 0.2]
        ref = scc_brute(n, edges)
        c1, comp1 = kosaraju(n, edges)
        c2, comp2 = tarjan_scc(n, edges)
        assert groups(comp1) == groups(comp2) == ref and c1 == c2 == len(ref)
    print("SCC 코사라주·타잔: 400개 그래프에서 도달 가능성 완전 계산과 일치")

    for _ in range(400):
        n = rng.randint(1, 10)
        edges = [(a, b) for a in range(n) for b in range(a + 1, n) if rng.random() < 0.3]
        edges += [rng.choice(edges)] if edges and rng.random() < 0.3 else []      # 다중 간선
        cut, bridges = cut_vertices_and_bridges(n, edges)
        base = n_components(n, edges)
        ref_cut = {v for v in range(n) if n_components(n, edges, skip_vertex=v) > base - (1 if all(v not in e for e in edges) else 0)}
        ref_br = sorted(tuple(sorted(e)) for i, e in enumerate(edges) if n_components(n, edges, skip_edge=i) > base)
        assert cut == ref_cut and bridges == ref_br, (n, edges, cut, ref_cut, bridges, ref_br)
    print("단절점·단절선: 400개 그래프(다중 간선 포함)에서 '지워 보고 연결 요소 세기'와 일치")

    for _ in range(400):
        n = rng.randint(1, 6)
        edges = [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randint(0, 7))]
        edges = [(a, b) for a, b in edges if a != b]
        p = euler_path(n, edges)
        assert (p is not None) == euler_brute(n, edges), (n, edges)
        if p and edges:
            left = sorted(tuple(sorted(e)) for e in edges)
            walked = sorted(tuple(sorted(e)) for e in zip(p, p[1:]))
            assert left == walked
    print("오일러 경로: 400개 그래프에서 완전 탐색과 존재 여부 일치, 모든 간선을 정확히 한 번 사용")

    # 예제
    e = [(0, 1), (1, 2), (2, 0), (1, 3), (3, 4), (4, 5), (5, 3), (5, 6)]
    print("SCC 예제:", sorted(sorted(s) for s in groups(tarjan_scc(7, e)[1])))
    ue = [(0, 1), (1, 2), (2, 0), (1, 3), (3, 4), (4, 5), (5, 3)]
    print("단절점·단절선 예제:", cut_vertices_and_bridges(6, ue))
    print("한붓그리기 예제(집 모양):", euler_path(5, [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2), (1, 3), (2, 4), (3, 4)]))
