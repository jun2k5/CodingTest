"""분기 한정법: 0-1 배낭(분수 배낭 상한)과 외판원 문제(최소 간선 하한)."""
import heapq, itertools, random


def knapsack_bnb(items, cap):
    """items = [(가치, 무게)]. 최적 가치와 확장한 노드 수."""
    items = sorted(items, key=lambda x: x[0] / x[1], reverse=True)   # 가치/무게 내림차순
    n = len(items)

    def bound(i, value, weight):
        """i번부터 남은 물건을 쪼개서라도 담는다고 칠 때의 상한(분수 배낭)."""
        b, w = value, weight
        while i < n and w + items[i][1] <= cap:
            b += items[i][0]; w += items[i][1]; i += 1
        if i < n:
            b += items[i][0] * (cap - w) / items[i][1]
        return b

    best, expanded = 0, 0
    heap = [(-bound(0, 0, 0), 0, 0, 0)]       # (-상한, 다음 물건, 가치, 무게): 상한이 큰 노드부터(최선 우선)
    while heap:
        neg_b, i, v, w = heapq.heappop(heap)
        if -neg_b <= best or i == n:
            continue                          # 상한이 지금까지 최선보다 나쁘면 버린다(한정)
        expanded += 1
        val, wt = items[i]
        if w + wt <= cap:                     # i번을 넣는 가지
            nv, nw = v + val, w + wt
            best = max(best, nv)
            b = bound(i + 1, nv, nw)
            if b > best: heapq.heappush(heap, (-b, i + 1, nv, nw))
        b = bound(i + 1, v, w)                # i번을 빼는 가지
        if b > best: heapq.heappush(heap, (-b, i + 1, v, w))
    return best, expanded


def knapsack_brute(items, cap):
    best = 0
    for m in range(1 << len(items)):
        w = sum(items[i][1] for i in range(len(items)) if m >> i & 1)
        if w <= cap:
            best = max(best, sum(items[i][0] for i in range(len(items)) if m >> i & 1))
    return best


def tsp_bnb(d):
    """깊이 우선 분기 한정. 하한 = 현재 비용 + 방문 안 한 도시마다 '나가는 최소 간선' 합."""
    n = len(d)
    min_out = [min(d[i][j] for j in range(n) if j != i) for i in range(n)]
    best, nodes = float("inf"), 0

    def go(city, visited, cost, count):
        nonlocal best, nodes
        nodes += 1
        if count == n:
            best = min(best, cost + d[city][0]); return
        lower = cost + min_out[city] + sum(min_out[j] for j in range(n) if not visited >> j & 1)
        if lower >= best:
            return                            # 이 가지는 아무리 잘해도 최선보다 못하다
        for nxt in sorted(range(n), key=lambda j: d[city][j]):   # 가까운 도시부터: 좋은 해를 빨리 찾아 가지치기 강화
            if not visited >> nxt & 1:
                go(nxt, visited | 1 << nxt, cost + d[city][nxt], count + 1)

    go(0, 1, 0, 1)
    return best, nodes


def tsp_brute(d):
    n = len(d)
    return min(sum(d[a][b] for a, b in zip((0,) + p, p + (0,))) for p in itertools.permutations(range(1, n)))


if __name__ == "__main__":
    rng = random.Random(53)
    for _ in range(300):
        items = [(rng.randint(1, 40), rng.randint(1, 20)) for _ in range(rng.randint(1, 12))]
        cap = rng.randint(1, 60)
        assert knapsack_bnb(items, cap)[0] == knapsack_brute(items, cap)
    print("배낭 분기 한정: 300개 입력에서 완전 탐색과 같은 최적값")
    items = [(rng.randint(10, 100), rng.randint(5, 50)) for _ in range(30)]
    best, expanded = knapsack_bnb(items, 300)
    print(f"물건 30개, 용량 300: 최적 가치 {best}, 확장 노드 {expanded:,}개 / 전체 조합 {2**30:,}개")

    for _ in range(50):
        n = rng.randint(2, 8)
        pts = [(rng.randint(0, 100), rng.randint(0, 100)) for _ in range(n)]
        d = [[abs(a[0] - b[0]) + abs(a[1] - b[1]) for b in pts] for a in pts]
        assert tsp_bnb(d)[0] == tsp_brute(d)
    print("TSP 분기 한정: 50개 입력에서 순열 완전 탐색과 같은 최적값")
    n = 11
    pts = [(rng.randint(0, 100), rng.randint(0, 100)) for _ in range(n)]
    d = [[abs(a[0] - b[0]) + abs(a[1] - b[1]) for b in pts] for a in pts]
    best, nodes = tsp_bnb(d)
    import math
    print(f"도시 {n}개: 최적 경로 {best}, 방문 노드 {nodes:,}개 / 순열 {math.factorial(n - 1):,}개")
