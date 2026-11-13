"""이진 최소 힙, 힙 정렬, heapq 비교."""
import sys, pathlib, random, heapq
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


def _sift_down(a, i, n, before):
    """자식 중 우선순위가 높은 쪽과 바꾸며 내려간다."""
    while True:
        l, r, best = 2 * i + 1, 2 * i + 2, i
        if l < n and before(a[l], a[best]): best = l
        if r < n and before(a[r], a[best]): best = r
        if best == i: return
        a[i], a[best] = a[best], a[i]
        i = best


class MinHeap:
    def __init__(self):
        self.a = []

    def push(self, x):
        a = self.a
        a.append(x)
        i = len(a) - 1
        while i > 0:                       # 부모보다 작으면 위로 올린다 (sift-up)
            p = (i - 1) // 2
            if a[p] <= a[i]: break
            a[p], a[i] = a[i], a[p]
            i = p

    def pop(self):
        a = self.a
        top = a[0]
        last = a.pop()
        if a:
            a[0] = last
            _sift_down(a, 0, len(a), lambda x, y: x < y)
        return top

    def __len__(self):
        return len(self.a)


def heapify_max(a):
    """아래쪽 내부 노드부터 sift-down 하는 O(n) 힙 만들기 (최대 힙)."""
    for i in range(len(a) // 2 - 1, -1, -1):
        _sift_down(a, i, len(a), lambda x, y: x > y)


def heap_sort(a):
    """제자리 힙 정렬. 최대 힙을 만든 뒤 루트를 끝으로 보낸다. 불안정, O(n log n), 추가 공간 O(1)."""
    heapify_max(a)
    for end in range(len(a) - 1, 0, -1):
        a[0], a[end] = a[end], a[0]
        _sift_down(a, 0, end, lambda x, y: x > y)


if __name__ == "__main__":
    from _check import check_sort
    check_sort(heap_sort)
    rng = random.Random(7)
    for _ in range(300):
        h, ref = MinHeap(), []
        for _ in range(rng.randint(1, 80)):
            if ref and rng.random() < 0.4:
                assert h.pop() == heapq.heappop(ref)
            else:
                x = rng.randint(-99, 99); h.push(x); heapq.heappush(ref, x)
    print("MinHeap: heapq와 300회 무작위 연산 결과 일치")
    a = [4, 10, 3, 5, 1]
    heapify_max(a)
    print("최대 힙 만들기 [4, 10, 3, 5, 1] ->", a)
    print("heapq.nlargest(3, [5, 1, 9, 3, 7, 8]) ->", heapq.nlargest(3, [5, 1, 9, 3, 7, 8]))
    mx = []
    for x in [5, 1, 9, 3]: heapq.heappush(mx, -x)
    print("부호를 뒤집은 최대 힙에서 pop ->", -heapq.heappop(mx))
