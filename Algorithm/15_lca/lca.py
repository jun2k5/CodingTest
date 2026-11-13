"""최소 공통 조상(LCA): 단순 방법과 이진 리프팅(희소 테이블)."""
import random
from collections import deque


def build(n, edges, root=0):
    g = [[] for _ in range(n)]
    for a, b in edges:
        g[a].append(b); g[b].append(a)
    parent, depth = [-1] * n, [0] * n
    seen = [False] * n
    q = deque([root]); seen[root] = True
    while q:                                     # BFS로 부모와 깊이를 구한다 (재귀 깊이 문제 없음)
        x = q.popleft()
        for y in g[x]:
            if not seen[y]:
                seen[y] = True; parent[y] = x; depth[y] = depth[x] + 1; q.append(y)
    return parent, depth


def lca_naive(parent, depth, a, b):
    while depth[a] > depth[b]: a = parent[a]
    while depth[b] > depth[a]: b = parent[b]
    while a != b: a, b = parent[a], parent[b]
    return a


class BinaryLifting:
    def __init__(self, parent, depth):
        n = len(parent)
        self.LOG = max(1, n.bit_length())
        self.depth = depth
        self.up = [[p if p != -1 else i for i, p in enumerate(parent)]]   # up[k][v] = v의 2^k번째 조상
        for k in range(1, self.LOG):
            prev = self.up[k - 1]
            self.up.append([prev[prev[v]] for v in range(n)])

    def lca(self, a, b):
        if self.depth[a] < self.depth[b]:
            a, b = b, a
        diff = self.depth[a] - self.depth[b]
        for k in range(self.LOG):                # 깊이 차이를 이진수로 나눠 한 번에 올린다
            if diff >> k & 1:
                a = self.up[k][a]
        if a == b:
            return a
        for k in range(self.LOG - 1, -1, -1):    # 조상이 달라지는 한 크게 함께 올린다
            if self.up[k][a] != self.up[k][b]:
                a, b = self.up[k][a], self.up[k][b]
        return self.up[0][a]


if __name__ == "__main__":
    rng = random.Random(43)
    for _ in range(300):
        n = rng.randint(1, 80)
        edges = [(i, rng.randrange(i)) for i in range(1, n)]
        parent, depth = build(n, edges)
        bl = BinaryLifting(parent, depth)
        for _ in range(50):
            a, b = rng.randrange(n), rng.randrange(n)
            assert bl.lca(a, b) == lca_naive(parent, depth, a, b)
    print("이진 리프팅 LCA: 300개 무작위 트리에서 단순 방법과 일치")
    edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (4, 6), (4, 7)]
    parent, depth = build(8, edges)
    bl = BinaryLifting(parent, depth)
    print("예제 트리 LCA(6, 3) =", bl.lca(6, 3), " LCA(7, 5) =", bl.lca(7, 5), " LCA(6, 7) =", bl.lca(6, 7))
    # 두 노드 사이 거리 = depth[a] + depth[b] - 2 * depth[lca]
    a, b = 6, 5
    print(f"노드 {a}와 {b} 사이 간선 수 =", depth[a] + depth[b] - 2 * depth[bl.lca(a, b)])
    n = 100_000
    chain = [(i, i - 1) for i in range(1, n)]
    parent, depth = build(n, chain)
    import time
    bl = BinaryLifting(parent, depth)
    t = time.perf_counter()
    for _ in range(1000): bl.lca(n - 1, n // 2)
    t1 = time.perf_counter() - t
    t = time.perf_counter()
    for _ in range(10): lca_naive(parent, depth, n - 1, n // 2)
    t2 = (time.perf_counter() - t) * 100
    print(f"일직선 트리 10만 노드, 질의 1000번: 이진 리프팅 {t1*1000:.1f}ms, 단순 방법(환산) {t2*1000:.0f}ms")
