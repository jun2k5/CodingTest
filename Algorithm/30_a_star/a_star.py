"""A* 탐색: f(n) = g(n) + h(n). 격자에서 맨해튼 거리 휴리스틱, 다익스트라와 확장 노드 수 비교."""
import heapq, random


def neighbors(grid, r, c):
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] != "#":
            yield nr, nc


def a_star(grid, start, goal, h):
    """반환: (최단 거리 또는 -1, 확장한 노드 수, 경로). h=lambda p: 0 이면 다익스트라와 같다."""
    g = {start: 0}
    prev = {start: None}
    pq = [(h(start), 0, start)]                    # (f, -g, 위치): f가 같으면 g가 큰(목표에 가까운) 쪽 먼저
    closed = set()
    expanded = 0
    while pq:
        f, neg_g, cur = heapq.heappop(pq)
        gc = -neg_g
        if cur in closed: continue
        closed.add(cur)
        expanded += 1
        if cur == goal:
            path = []
            while cur is not None: path.append(cur); cur = prev[cur]
            return gc, expanded, path[::-1]
        for nxt in neighbors(grid, *cur):
            ng = gc + 1
            if ng < g.get(nxt, float("inf")):
                g[nxt] = ng; prev[nxt] = cur
                heapq.heappush(pq, (ng + h(nxt), -ng, nxt))
    return -1, expanded, None


def manhattan(goal, scale=1):
    return lambda p: scale * (abs(p[0] - goal[0]) + abs(p[1] - goal[1]))


def random_grid(rng, n, m, wall):
    grid = [["#" if rng.random() < wall else "." for _ in range(m)] for _ in range(n)]
    return grid


def bfs_dist(grid, s, t):
    from collections import deque
    d = {s: 0}; q = deque([s])
    while q:
        v = q.popleft()
        if v == t: return d[v]
        for u in neighbors(grid, *v):
            if u not in d: d[u] = d[v] + 1; q.append(u)
    return -1


if __name__ == "__main__":
    rng = random.Random(30)
    worse = 0
    trials = 500
    for _ in range(trials):
        n, m = rng.randint(2, 15), rng.randint(2, 15)
        grid = random_grid(rng, n, m, 0.25)
        s = (rng.randrange(n), rng.randrange(m)); t = (rng.randrange(n), rng.randrange(m))
        grid[s[0]][s[1]] = grid[t[0]][t[1]] = "."
        ref = bfs_dist(grid, s, t)
        d0, _, _ = a_star(grid, s, t, lambda p: 0)
        d1, _, path = a_star(grid, s, t, manhattan(t))
        assert d0 == d1 == ref
        if path: assert len(path) - 1 == ref
        d3, _, _ = a_star(grid, s, t, manhattan(t, 3))   # 허용적이지 않은 휴리스틱
        assert d3 >= ref
        worse += d3 > ref
    print(f"A*(맨해튼)·다익스트라(h=0): {trials}개 격자에서 BFS 최단 거리와 일치")
    print(f"h = 3 x 맨해튼(과대 추정): {trials}개 중 {worse}개에서 최단보다 긴 경로를 반환")

    # 확장 노드 수 비교
    for size, wall in ((50, 0.0), (50, 0.2), (200, 0.2)):
        r2 = random.Random(size)
        tot = [0, 0, 0]
        for _ in range(20):
            grid = random_grid(r2, size, size, wall)
            s, t = (0, 0), (size - 1, size - 1)
            grid[0][0] = grid[size - 1][size - 1] = "."
            a, e0, _ = a_star(grid, s, t, lambda p: 0)
            b, e1, _ = a_star(grid, s, t, manhattan(t))
            c, e3, _ = a_star(grid, s, t, manhattan(t, 3))
            tot[0] += e0; tot[1] += e1; tot[2] += e3
        print(f"{size}x{size} 격자, 벽 {int(wall * 100)}%, 왼쪽 위→오른쪽 아래 20회 평균 확장 노드: "
              f"다익스트라 {tot[0] // 20:,} / A* {tot[1] // 20:,} / 3x맨해튼 {tot[2] // 20:,}")

    # 작은 예제
    maze = [list(row) for row in (
        ".....",
        ".###.",
        "...#.",
        "#.#..",
        "...#.",
    )]
    d, e, path = a_star(maze, (0, 0), (4, 4), manhattan((4, 4)))
    print("5x5 미로 (0,0)→(4,4): 거리", d, "확장", e, "경로", path)
