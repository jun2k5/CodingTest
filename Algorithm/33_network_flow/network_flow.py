"""네트워크 플로우: 포드-풀커슨(DFS 증가 경로), 에드몬드-카프(BFS 증가 경로), 최대 유량 최소 컷."""
import itertools, random
from collections import deque


class Flow:
    """간선마다 역방향 간선을 함께 만든다. 역방향 용량 = 이미 보낸 유량 = 되돌릴 수 있는 양."""

    def __init__(self, n):
        self.n = n
        self.g = [[] for _ in range(n)]           # g[v] = 간선 번호 목록
        self.to, self.cap = [], []

    def add_edge(self, a, b, c):
        self.g[a].append(len(self.to)); self.to.append(b); self.cap.append(c)
        self.g[b].append(len(self.to)); self.to.append(a); self.cap.append(0)

    def ford_fulkerson(self, s, t):
        """아무 증가 경로나(DFS) 찾아 병목만큼 흘린다. 정수 용량이면 O(E·f)."""
        flow, aug = 0, 0
        while True:
            seen = [False] * self.n
            def dfs(v, f):
                if v == t: return f
                seen[v] = True
                for e in self.g[v]:
                    u = self.to[e]
                    if self.cap[e] > 0 and not seen[u]:
                        d = dfs(u, min(f, self.cap[e]))
                        if d:
                            self.cap[e] -= d; self.cap[e ^ 1] += d
                            return d
                return 0
            pushed = dfs(s, float("inf"))
            if not pushed: return flow, aug
            flow += pushed; aug += 1

    def edmonds_karp(self, s, t):
        """BFS로 간선 수가 가장 적은 증가 경로를 고른다. O(V·E²), 용량 크기와 무관."""
        flow, aug = 0, 0
        while True:
            prev = [-1] * self.n
            prev[s] = -2
            q = deque([s])
            while q and prev[t] == -1:
                v = q.popleft()
                for e in self.g[v]:
                    u = self.to[e]
                    if self.cap[e] > 0 and prev[u] == -1:
                        prev[u] = e; q.append(u)
            if prev[t] == -1: return flow, aug
            f, v = float("inf"), t
            while v != s:                         # 병목 찾기
                e = prev[v]; f = min(f, self.cap[e]); v = self.to[e ^ 1]
            v = t
            while v != s:
                e = prev[v]; self.cap[e] -= f; self.cap[e ^ 1] += f; v = self.to[e ^ 1]
            flow += f; aug += 1

    def min_cut_side(self, s):
        """최대 유량을 흘린 뒤 잔여 그래프에서 s로 갈 수 있는 정점 집합 S. S→T 간선들이 최소 컷."""
        seen = [False] * self.n; seen[s] = True
        q = deque([s])
        while q:
            v = q.popleft()
            for e in self.g[v]:
                if self.cap[e] > 0 and not seen[self.to[e]]:
                    seen[self.to[e]] = True; q.append(self.to[e])
        return seen


def brute_min_cut(n, edges, s, t):
    """s를 포함하고 t를 포함하지 않는 모든 정점 집합 S에 대해 S→T 용량 합의 최솟값."""
    others = [v for v in range(n) if v not in (s, t)]
    best = float("inf")
    for k in range(len(others) + 1):
        for comb in itertools.combinations(others, k):
            S = set(comb) | {s}
            best = min(best, sum(c for a, b, c in edges if a in S and b not in S))
    return best


def build(n, edges):
    f = Flow(n)
    for a, b, c in edges: f.add_edge(a, b, c)
    return f


if __name__ == "__main__":
    rng = random.Random(33)
    for _ in range(300):
        n = rng.randint(2, 8)
        edges = [(a, b, rng.randint(1, 10)) for a in range(n) for b in range(n) if a != b and rng.random() < 0.35]
        s, t = 0, n - 1
        ref = brute_min_cut(n, edges, s, t)
        f1, _ = build(n, edges).ford_fulkerson(s, t)
        fl = build(n, edges)
        f2, _ = fl.edmonds_karp(s, t)
        S = fl.min_cut_side(s)
        cut = sum(c for a, b, c in edges if S[a] and not S[b])
        assert f1 == f2 == ref == cut and not S[t]
    print("포드-풀커슨·에드몬드-카프 최대 유량 = 완전 탐색 최소 컷 = 잔여 그래프 컷 (300개 그래프)")

    # 교과서 예제 (CLRS 26.1): s=0, v1..v4, t=5
    e = [(0, 1, 16), (0, 2, 13), (2, 1, 4), (1, 3, 12), (3, 2, 9), (2, 4, 14), (4, 3, 7), (3, 5, 20), (4, 5, 4)]
    fl = build(6, e)
    f, aug = fl.edmonds_karp(0, 5)
    S = fl.min_cut_side(0)
    print("예제 최대 유량:", f, "증가 경로", aug, "번 / 최소 컷 S =", [v for v in range(6) if S[v]],
          "컷 간선 =", [(a, b, c) for a, b, c in e if S[a] and not S[b]])

    # 증가 경로를 나쁘게 고르면: 가운데 용량 1 간선을 정방향·역방향으로 번갈아 타는 두 경로를 교대로 고른다
    C = 10000
    e = [(0, 1, C), (0, 2, C), (1, 2, 1), (1, 3, C), (2, 3, C)]
    fl = build(4, e)
    # k번째로 추가한 간선의 번호는 2k, 그 역방향은 2k+1
    paths = [[0, 4, 8],                            # 0→1, 1→2, 2→3
             [2, 5, 6]]                            # 0→2, 2→1(1→2의 역방향), 1→3
    flow = aug = 0
    while True:
        ids = paths[aug % 2]
        f = min(fl.cap[x] for x in ids)
        if f == 0: break
        for x in ids: fl.cap[x] -= f; fl.cap[x ^ 1] += f
        flow += f; aug += 1
    rest, _ = fl.edmonds_karp(0, 3)                # 남은 증가 경로로 마저 흘린다
    _, aug_ek = build(4, e).edmonds_karp(0, 3)
    print(f"용량 {C} 그래프(가운데 간선 1): 최대 유량 {flow + rest}, 번갈아 고른 증가 경로 {aug:,}번, 에드몬드-카프 {aug_ek}번")
