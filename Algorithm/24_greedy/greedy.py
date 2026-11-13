"""그리디: 활동 선택(회의실 배정), 분할 가능한 배낭, 허프만 코딩, 동전 거스름돈 반례."""
import heapq, itertools, random


def activity_selection(intervals):
    """끝나는 시간이 빠른 것부터 고른다. 같으면 시작이 빠른 것 먼저(길이 0 구간 처리)."""
    chosen, end = [], float("-inf")
    for s, e in sorted(intervals, key=lambda x: (x[1], x[0])):
        if s >= end:
            chosen.append((s, e)); end = e
    return chosen


def activity_brute(intervals):
    best = 0
    for k in range(len(intervals), 0, -1):
        for c in itertools.combinations(sorted(intervals), k):
            if all(c[i][1] <= c[i + 1][0] for i in range(len(c) - 1)):
                return k
    return 0


def fractional_knapsack(items, cap):
    """items = [(가치, 무게)]. 무게당 가치가 높은 순서로, 마지막은 쪼개서 담는다."""
    total = 0.0
    for v, w in sorted(items, key=lambda x: x[0] / x[1], reverse=True):
        if cap <= 0: break
        take = min(w, cap)
        total += v * take / w
        cap -= take
    return total


def huffman(freq):
    """빈도가 가장 작은 두 노드를 합치는 것을 반복. 문자별 코드 반환."""
    heap = [(f, i, ch) for i, (ch, f) in enumerate(sorted(freq.items()))]
    heapq.heapify(heap)
    if len(heap) == 1:
        return {heap[0][2]: "0"}
    cnt = len(heap)
    while len(heap) > 1:
        f1, _, a = heapq.heappop(heap)
        f2, _, b = heapq.heappop(heap)
        heapq.heappush(heap, (f1 + f2, cnt, (a, b))); cnt += 1     # 순번으로 동점 처리
    codes = {}
    def walk(node, code):
        if isinstance(node, tuple):
            walk(node[0], code + "0"); walk(node[1], code + "1")
        else:
            codes[node] = code
    walk(heap[0][2], "")
    return codes


def coin_greedy(coins, amount):
    cnt = 0
    for c in sorted(coins, reverse=True):
        cnt += amount // c; amount %= c
    return cnt if amount == 0 else -1


def coin_dp(coins, amount):
    INF = float("inf")
    dp = [0] + [INF] * amount
    for x in range(1, amount + 1):
        dp[x] = min((dp[x - c] + 1 for c in coins if c <= x), default=INF)
    return dp[amount]


if __name__ == "__main__":
    rng = random.Random(83)
    for _ in range(300):
        iv = []
        for _ in range(rng.randint(0, 9)):
            s = rng.randint(0, 20); iv.append((s, s + rng.randint(0, 6)))
        assert len(activity_selection(iv)) == activity_brute(iv)
    print("활동 선택: 300개 입력에서 완전 탐색과 같은 최대 개수")
    meetings = [(1, 4), (3, 5), (0, 6), (5, 7), (3, 8), (5, 9), (6, 10), (8, 11), (8, 12), (2, 13), (12, 14)]
    print("백준 1931 예제 ->", len(activity_selection(meetings)), "개:", activity_selection(meetings))

    print("분할 배낭 [(60,10),(100,20),(120,30)] 용량 50 ->", fractional_knapsack([(60, 10), (100, 20), (120, 30)], 50))
    print("  (같은 문제를 0-1 배낭으로 풀면 220. 쪼갤 수 없으면 그리디가 틀린다)")

    freq = {"a": 45, "b": 13, "c": 12, "d": 16, "e": 9, "f": 5}
    codes = huffman(freq)
    bits = sum(freq[c] * len(codes[c]) for c in freq)
    print("허프만 코드:", dict(sorted(codes.items())), f"총 {bits}비트 (고정 3비트면 {3 * sum(freq.values())}비트)")
    codes_list = list(codes.values())
    assert not any(a != b and b.startswith(a) for a in codes_list for b in codes_list)
    print("  어떤 코드도 다른 코드의 접두사가 아님(접두사 코드) 확인")

    print("동전 [500,100,50,10]으로 1260원: 그리디", coin_greedy([500, 100, 50, 10], 1260), "개 / DP", coin_dp([500, 100, 50, 10], 1260), "개")
    print("동전 [1,3,4]로 6원:            그리디", coin_greedy([1, 3, 4], 6), "개 / DP", coin_dp([1, 3, 4], 6), "개")
    print("동전 [1,5,10,16]으로 20원:     그리디", coin_greedy([1, 5, 10, 16], 20), "개 / DP", coin_dp([1, 5, 10, 16], 20), "개")
