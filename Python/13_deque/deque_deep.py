"""13. deque: 양방향 큐, maxlen, rotate, BFS, 슬라이딩 윈도우, list와 성능 비교"""
import timeit
from collections import deque


def basics():
    dq = deque([2, 3])
    dq.appendleft(1)
    dq.append(4)
    dq.extendleft([0, -1])           # 하나씩 왼쪽에 넣으므로 순서가 뒤집힌다
    print("deque:", dq)
    print("popleft/pop:", dq.popleft(), dq.pop(), "| 남은 것:", dq)
    assert list(dq) == [0, 1, 2, 3]
    print("인덱스 접근:", dq[0], dq[-1], "| 중간 인덱스는 O(n)")


def bounded():
    recent = deque(maxlen=3)
    for page in ["home", "list", "item1", "item2", "cart"]:
        recent.append(page)          # 꽉 차면 반대쪽에서 자동으로 버린다
    print("최근 3개:", list(recent))
    assert list(recent) == ["item1", "item2", "cart"]

    with open(__file__, encoding="utf-8") as f:
        tail = deque(f, maxlen=2)    # 파일의 마지막 두 줄(tail)
    print("파일 마지막 줄 수:", len(tail))


def rotate():
    dq = deque(range(5))
    dq.rotate(2)
    print("rotate(2):", list(dq))
    dq.rotate(-3)
    print("rotate(-3):", list(dq))
    assert list(dq) == [1, 2, 3, 4, 0]


def bfs():
    grid = [
        "S.#",
        "..#",
        "#.E",
    ]
    start, goal = (0, 0), (2, 2)
    queue = deque([(start, 0)])
    seen = {start}
    while queue:
        (r, c), dist = queue.popleft()
        if (r, c) == goal:
            print("BFS 최단 거리:", dist)
            assert dist == 4
            return
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < 3 and 0 <= nc < 3 and grid[nr][nc] != "#" and (nr, nc) not in seen:
                seen.add((nr, nc))
                queue.append(((nr, nc), dist + 1))


def sliding_window_max(nums, k):
    """단조 감소 deque에 인덱스를 담아 각 윈도우 최댓값을 O(n)에"""
    dq, result = deque(), []
    for i, v in enumerate(nums):
        while dq and nums[dq[-1]] <= v:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            result.append(nums[dq[0]])
    return result


def performance():
    n = 50_000
    t_list = timeit.timeit("q.insert(0, 1); q.pop(0)", setup=f"q=list(range({n}))", number=20_000)
    t_deque = timeit.timeit("q.appendleft(1); q.popleft()",
                            setup=f"from collections import deque; q=deque(range({n}))", number=20_000)
    print(f"왼쪽 넣고 빼기 2만 번 - list: {t_list * 1000:.1f}ms, deque: {t_deque * 1000:.2f}ms")
    assert t_list > t_deque


if __name__ == "__main__":
    basics()
    bounded()
    rotate()
    bfs()
    print("슬라이딩 윈도우 최댓값:", sliding_window_max([1, 3, -1, -3, 5, 3, 6, 7], 3))
    assert sliding_window_max([1, 3, -1, -3, 5, 3, 6, 7], 3) == [3, 3, 5, 5, 6, 7]
    performance()
    print("모든 검증 통과")
