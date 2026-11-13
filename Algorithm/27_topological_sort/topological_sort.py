"""위상 정렬: 칸(Kahn) 알고리즘, DFS 방식, 사이클 판정."""
import heapq, itertools, random
from collections import deque


def kahn(n, edges):
    """진입 차수 0인 정점부터 꺼낸다. 사이클이 있으면 None."""
    g = [[] for _ in range(n)]
    indeg = [0] * n
    for a, b in edges:
        g[a].append(b); indeg[b] += 1
    q = deque(v for v in range(n) if indeg[v] == 0)
    order = []
    while q:
        v = q.popleft(); order.append(v)
        for u in g[v]:
            indeg[u] -= 1
            if indeg[u] == 0: q.append(u)
    return order if len(order) == n else None


def kahn_smallest(n, edges):
    """여러 답 중 사전순으로 가장 앞선 순서: 큐 대신 최소 힙."""
    g = [[] for _ in range(n)]
    indeg = [0] * n
    for a, b in edges:
        g[a].append(b); indeg[b] += 1
    h = [v for v in range(n) if indeg[v] == 0]
    heapq.heapify(h)
    order = []
    while h:
        v = heapq.heappop(h); order.append(v)
        for u in g[v]:
            indeg[u] -= 1
            if indeg[u] == 0: heapq.heappush(h, u)
    return order if len(order) == n else None


def dfs_topo(n, edges):
    """DFS가 끝나는 순서(후위)를 뒤집으면 위상 순서. 회색(방문 중) 정점을 다시 만나면 사이클."""
    g = [[] for _ in range(n)]
    for a, b in edges: g[a].append(b)
    WHITE, GRAY, BLACK = 0, 1, 2
    color, post = [WHITE] * n, []
    for s in range(n):
        if color[s] != WHITE: continue
        stack = [(s, 0)]
        color[s] = GRAY
        while stack:                              # 반복 DFS: (정점, 다음에 볼 이웃 인덱스)
            v, i = stack[-1]
            if i < len(g[v]):
                stack[-1] = (v, i + 1)
                u = g[v][i]
                if color[u] == GRAY: return None   # 뒤로 가는 간선 = 사이클
                if color[u] == WHITE:
                    color[u] = GRAY; stack.append((u, 0))
            else:
                color[v] = BLACK; post.append(v); stack.pop()
    return post[::-1]


def is_valid_order(n, edges, order):
    pos = {v: i for i, v in enumerate(order)}
    return len(order) == n and len(pos) == n and all(pos[a] < pos[b] for a, b in edges)


def brute_has_order(n, edges):
    return any(is_valid_order(n, edges, p) for p in itertools.permutations(range(n)))


def longest_path_dag(n, edges, cost):
    """위상 순서대로 DP: 작업 v를 끝내는 가장 이른 시각 (선행 작업이 모두 끝나야 시작)."""
    order = kahn(n, edges)
    finish = cost[:]
    g = [[] for _ in range(n)]
    for a, b in edges: g[a].append(b)
    for v in order:
        for u in g[v]:
            finish[u] = max(finish[u], finish[v] + cost[u])
    return finish


if __name__ == "__main__":
    rng = random.Random(27)
    for _ in range(400):
        n = rng.randint(1, 7)
        edges = list({(a, b) for a in range(n) for b in range(n) if a != b and rng.random() < 0.2})
        exists = brute_has_order(n, edges)
        for f in (kahn, kahn_smallest, dfs_topo):
            o = f(n, edges)
            assert (o is not None) == exists, (f.__name__, n, edges)
            if o is not None: assert is_valid_order(n, edges, o)
        if exists:
            best = min(p for p in itertools.permutations(range(n)) if is_valid_order(n, edges, p))
            assert tuple(kahn_smallest(n, edges)) == best
    print("칸·DFS 위상 정렬, 사이클 판정, 사전순 최소 순서: 400개 그래프에서 완전 탐색과 일치")

    # 백준 2252 예제 (1번부터 → 0번부터로 바꿈): 3명, 1→3, 2→3
    print("백준 2252 예제 1:", [v + 1 for v in kahn(3, [(0, 2), (1, 2)])])
    # 예제 2: 4명, 4→2, 3→1
    print("백준 2252 예제 2:", [v + 1 for v in kahn(4, [(3, 1), (2, 0)])])

    e = [(0, 1), (1, 2), (2, 0), (2, 3)]
    print("사이클 0→1→2→0 포함:", kahn(4, e), dfs_topo(4, e))

    # 과목 선수 관계 예제
    names = ["자료구조", "알고리즘", "운영체제", "컴퓨터구조", "컴파일러"]
    pre = [(0, 1), (3, 2), (0, 2), (1, 4)]
    print("선수 과목 순서(칸):", [names[v] for v in kahn(5, pre)])
    print("선수 과목 순서(DFS):", [names[v] for v in dfs_topo(5, pre)])

    # 작업 완료 시각 (백준 1005 ACM Craft 예제 1)
    cost = [10, 1, 100, 10]
    print("ACM Craft 예제 1, 4번 건물 완성 시각:", longest_path_dag(4, [(0, 1), (0, 2), (1, 3), (2, 3)], cost)[3])
