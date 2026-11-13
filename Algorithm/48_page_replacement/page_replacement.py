"""페이지 교체: FIFO, LRU, OPT, LFU, 클럭(2차 기회). 벨레이디의 이상 현상. O(1) LRU 캐시."""
import random
from collections import OrderedDict, deque


def fifo(refs, frames):
    mem, q, faults = set(), deque(), 0
    for p in refs:
        if p in mem: continue
        faults += 1
        if len(mem) == frames:
            mem.discard(q.popleft())               # 가장 먼저 들어온 페이지
        mem.add(p); q.append(p)
    return faults


def lru(refs, frames):
    mem, faults = OrderedDict(), 0
    for p in refs:
        if p in mem:
            mem.move_to_end(p); continue           # 최근에 썼다고 표시
        faults += 1
        if len(mem) == frames:
            mem.popitem(last=False)                # 가장 오래전에 쓴 페이지
        mem[p] = True
    return faults


def opt(refs, frames):
    """앞으로 가장 늦게 쓰일(또는 다시 안 쓰일) 페이지를 내보낸다. 미래를 알아야 해서 실제로는 불가능, 비교 기준."""
    n = len(refs)
    nxt, last = [0] * n, {}
    for i in range(n - 1, -1, -1):                 # 각 위치에서 같은 페이지가 다음에 나오는 위치
        nxt[i] = last.get(refs[i], float("inf")); last[refs[i]] = i
    mem, faults = {}, 0                            # 페이지 -> 다음 사용 위치
    for i, p in enumerate(refs):
        if p in mem:
            mem[p] = nxt[i]; continue
        faults += 1
        if len(mem) == frames:
            victim = max(mem, key=mem.get)
            del mem[victim]
        mem[p] = nxt[i]
    return faults


def lfu(refs, frames):
    """사용 횟수가 가장 적은 페이지. 같으면 먼저 들어온 것."""
    mem, cnt, t, faults = {}, {}, 0, 0
    for p in refs:
        t += 1
        if p in mem:
            cnt[p] += 1; continue
        faults += 1
        if len(mem) == frames:
            victim = min(mem, key=lambda x: (cnt[x], mem[x]))
            del mem[victim]; del cnt[victim]
        mem[p], cnt[p] = t, 1
    return faults


def clock(refs, frames):
    """FIFO + 참조 비트. 시곗바늘이 가리키는 페이지의 비트가 1이면 0으로 바꾸고 넘어간다(2차 기회)."""
    slots, ref, hand, pos, faults = [None] * frames, [0] * frames, 0, {}, 0
    for p in refs:
        if p in pos:
            ref[pos[p]] = 1; continue
        faults += 1
        while slots[hand] is not None and ref[hand]:
            ref[hand] = 0; hand = (hand + 1) % frames
        if slots[hand] is not None: del pos[slots[hand]]
        slots[hand], ref[hand], pos[p] = p, 1, hand
        hand = (hand + 1) % frames
    return faults


def lru_naive(refs, frames):
    mem, faults = [], 0
    for p in refs:
        if p in mem:
            mem.remove(p); mem.append(p); continue
        faults += 1
        if len(mem) == frames: mem.pop(0)
        mem.append(p)
    return faults


class Node:
    __slots__ = ("key", "val", "prev", "next")
    def __init__(self, key=None, val=None):
        self.key, self.val, self.prev, self.next = key, val, None, None


class LRUCache:
    """해시 + 이중 연결 리스트. get/put 모두 O(1). 머리 쪽이 가장 최근, 꼬리 쪽이 가장 오래됨."""

    def __init__(self, capacity):
        self.cap, self.map = capacity, {}
        self.head, self.tail = Node(), Node()      # 더미 노드
        self.head.next, self.tail.prev = self.tail, self.head

    def _remove(self, node):
        node.prev.next, node.next.prev = node.next, node.prev

    def _push_front(self, node):
        node.prev, node.next = self.head, self.head.next
        self.head.next.prev = node; self.head.next = node

    def get(self, key):
        node = self.map.get(key)
        if node is None: return -1
        self._remove(node); self._push_front(node)
        return node.val

    def put(self, key, val):
        if key in self.map:
            node = self.map[key]; node.val = val
            self._remove(node); self._push_front(node)
            return
        if len(self.map) == self.cap:
            old = self.tail.prev
            self._remove(old); del self.map[old.key]
        node = Node(key, val)
        self.map[key] = node; self._push_front(node)


if __name__ == "__main__":
    rng = random.Random(48)
    for _ in range(2000):
        refs = [rng.randint(0, 7) for _ in range(rng.randint(0, 40))]
        f = rng.randint(1, 5)
        assert lru(refs, f) == lru_naive(refs, f)
        o = opt(refs, f)
        assert o <= min(fifo(refs, f), lru(refs, f), lfu(refs, f), clock(refs, f))
    print("LRU(OrderedDict) = LRU(리스트 직접 구현), OPT ≤ FIFO·LRU·LFU·클럭: 2000개 참조열에서 확인")

    # OPT가 실제 최소인지: 작은 입력에서 모든 교체 선택을 탐색
    def opt_brute(refs, frames):
        best = [float("inf")]
        def go(i, mem, faults):
            if faults >= best[0]: return
            if i == len(refs): best[0] = faults; return
            p = refs[i]
            if p in mem: go(i + 1, mem, faults); return
            if len(mem) < frames: go(i + 1, mem | {p}, faults + 1); return
            for v in mem: go(i + 1, (mem - {v}) | {p}, faults + 1)
        go(0, frozenset(), 0)
        return best[0]
    for _ in range(300):
        refs = [rng.randint(0, 5) for _ in range(rng.randint(0, 14))]
        f = rng.randint(1, 4)
        assert opt(refs, f) == opt_brute(refs, f)
    print("OPT: 300개 참조열에서 모든 교체 선택 완전 탐색의 최소 부재 수와 일치")

    refs = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
    print("참조열", refs, "프레임 3:")
    for name, f in (("FIFO", fifo), ("LRU", lru), ("OPT", opt), ("LFU", lfu), ("클럭", clock)):
        print(f"  {name}: 페이지 부재 {f(refs, 3)}번")

    belady = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    print("벨레이디의 이상 참조열", belady)
    for fr in (1, 2, 3, 4, 5):
        print(f"  프레임 {fr}: FIFO {fifo(belady, fr)}, LRU {lru(belady, fr)}, OPT {opt(belady, fr)}")
    anomalies = 0
    for _ in range(3000):
        refs = [rng.randint(0, 5) for _ in range(20)]
        for fr in range(1, 6):
            assert lru(refs, fr + 1) <= lru(refs, fr) and opt(refs, fr + 1) <= opt(refs, fr)
            anomalies += fifo(refs, fr + 1) > fifo(refs, fr)
    print(f"무작위 참조열 3000개 × 프레임 1~5: LRU·OPT는 프레임을 늘려 부재가 늘어난 경우 0번, FIFO는 {anomalies}번")

    # 지역성이 있는 참조열에서 비교: 80%는 작은 작업 집합, 20%는 전체에서
    hot = list(range(10))
    refs = [rng.choice(hot) if rng.random() < 0.8 else rng.randint(0, 99) for _ in range(20000)]
    print("지역성 있는 참조열 20,000개(페이지 100개, 80%는 10개에 집중), 프레임 12:")
    for name, f in (("FIFO", fifo), ("LRU", lru), ("LFU", lfu), ("클럭", clock), ("OPT", opt)):
        print(f"  {name}: 부재율 {100 * f(refs, 12) / len(refs):.1f}%")

    # LRU 캐시 검증: OrderedDict 기반 참조 구현과 동작 비교
    for _ in range(300):
        cap = rng.randint(1, 5)
        c, ref = LRUCache(cap), OrderedDict()
        for _ in range(100):
            k = rng.randint(0, 8)
            if rng.random() < 0.5:
                exp = ref[k] if k in ref else -1
                if k in ref: ref.move_to_end(k)
                assert c.get(k) == exp
            else:
                v = rng.randint(0, 99)
                c.put(k, v)
                if k in ref: ref.move_to_end(k)
                ref[k] = v
                if len(ref) > cap: ref.popitem(last=False)
    print("LRUCache(해시 + 이중 연결 리스트): 300개 무작위 연산열에서 OrderedDict 구현과 같은 결과")
    c = LRUCache(2)
    c.put(1, 1); c.put(2, 2); r1 = c.get(1); c.put(3, 3); r2 = c.get(2); c.put(4, 4)
    print("LRUCache(2): put(1) put(2) get(1)=", r1, "put(3) get(2)=", r2, "put(4) get(1)=", c.get(1), "get(3)=", c.get(3), "get(4)=", c.get(4))
