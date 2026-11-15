"""17. heapq 심화: 힙 불변식, heapify O(n), 동점 처리, pushpop·replace, nlargest·merge, 최대 힙(3.14)"""
import heapq
import itertools
import sys
from dataclasses import dataclass, field


def invariant():
    data = [9, 4, 7, 1, 8, 2]
    heapq.heapify(data)                      # 제자리, O(n)
    print("heapify 결과(리스트):", data)
    ok = all(data[i] <= data[c] for i in range(len(data)) for c in (2 * i + 1, 2 * i + 2) if c < len(data))
    print("불변식 heap[k] <= heap[2k+1], heap[2k+2]:", ok)
    print("최솟값은 항상 [0]:", data[0], "| 정렬된 건 아니다:", data != sorted(data))
    print("하나씩 꺼내면 정렬:", [heapq.heappop(data) for _ in range(len(data))])


def tie_breaking():
    tasks = []
    heapq.heappush(tasks, (1, "write", {"id": 1}))
    try:
        heapq.heappush(tasks, (1, "write", {"id": 2}))   # 앞 두 값이 같으면 dict끼리 비교
    except TypeError as e:
        print("동점 비교 실패:", e)

    counter = itertools.count()
    safe = []
    for priority, payload in [(2, {"n": "b"}), (1, {"n": "a"}), (1, {"n": "c"})]:
        heapq.heappush(safe, (priority, next(counter), payload))
    print("순번으로 동점 해결(FIFO):", [heapq.heappop(safe)[2]["n"] for _ in range(3)])


@dataclass(order=True)
class Job:
    priority: int
    seq: int
    name: str = field(compare=False)


def dataclass_entries():
    jobs = [Job(2, 0, "backup"), Job(1, 1, "email"), Job(1, 2, "sms")]
    heapq.heapify(jobs)
    print("dataclass(order=True) 항목:", [heapq.heappop(jobs).name for _ in range(3)])


def pushpop_replace():
    h = [1, 5, 9]
    print("heappushpop(h, 0):", heapq.heappushpop(h, 0), h)      # 넣고 나서 꺼냄 → 0이 바로 나옴
    print("heapreplace(h, 0):", heapq.heapreplace(h, 0), h)      # 꺼내고 나서 넣음


def top_k():
    scores = [37, 91, 12, 88, 65, 99, 3, 74]
    print("nlargest(3):", heapq.nlargest(3, scores), "| nsmallest(2):", heapq.nsmallest(2, scores))
    words = ["kiwi", "banana", "fig", "cherry"]
    print("key 사용:", heapq.nlargest(2, words, key=len))

    window, k = [], 3                                         # 스트림에서 상위 k개 유지
    for s in scores:
        if len(window) < k:
            heapq.heappush(window, s)
        elif s > window[0]:
            heapq.heapreplace(window, s)
    print("스트림 상위 3:", sorted(window, reverse=True))
    assert sorted(window, reverse=True) == [99, 91, 88]


def merge_sorted():
    a, b, c = [1, 4, 9], [2, 3, 10], [5, 6]
    merged = heapq.merge(a, b, c)
    print("merge(지연):", list(merged))
    logs1 = [("09:00", "a"), ("09:05", "c")]
    logs2 = [("09:01", "b"), ("09:07", "d")]
    print("시간순 병합:", [x[1] for x in heapq.merge(logs1, logs2, key=lambda x: x[0])])


def max_heap():
    nums = [3, 1, 4, 1, 5]
    neg = [-n for n in nums]
    heapq.heapify(neg)
    print("음수 트릭:", -heapq.heappop(neg))
    if sys.version_info >= (3, 14):
        h = nums[:]
        heapq.heapify_max(h)
        heapq.heappush_max(h, 9)
        print("3.14 heapify_max/heappush_max:", heapq.heappop_max(h), heapq.heappop_max(h))


def dijkstra():
    graph = {"A": {"B": 4, "C": 1}, "C": {"B": 2, "D": 5}, "B": {"D": 1}, "D": {}}
    dist = {"A": 0}
    pq = [(0, "A")]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist.get(u, float("inf")):
            continue                                 # 지연 삭제: 낡은 항목 건너뛰기
        for v, w in graph[u].items():
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    print("다익스트라:", dist)
    assert dist == {"A": 0, "C": 1, "B": 3, "D": 4}


if __name__ == "__main__":
    invariant()
    tie_breaking()
    dataclass_entries()
    pushpop_replace()
    top_k()
    merge_sorted()
    max_heap()
    dijkstra()
    print("모든 검증 통과")
