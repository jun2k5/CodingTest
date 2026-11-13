"""분산·확률적 자료구조: 일관된 해싱(가상 노드), 블룸 필터, 스킵 리스트."""
import bisect, hashlib, math, random, statistics


def h64(s: str) -> int:
    return int.from_bytes(hashlib.md5(s.encode()).digest()[:8], "big")


# ---------- 일관된 해싱 ----------

class ConsistentHash:
    """서버와 키를 같은 원(0 ~ 2^64-1) 위에 해시로 놓고, 키는 시계 방향으로 처음 만나는 서버에 배정한다.
    서버 하나를 원 위 여러 점(가상 노드)으로 놓으면 부하가 고르게 퍼진다."""

    def __init__(self, vnodes=100):
        self.vnodes, self.ring, self.owner = vnodes, [], {}

    def add(self, server):
        for i in range(self.vnodes):
            p = h64(f"{server}#{i}")
            bisect.insort(self.ring, p); self.owner[p] = server

    def remove(self, server):
        for i in range(self.vnodes):
            p = h64(f"{server}#{i}")
            self.ring.remove(p); del self.owner[p]

    def get(self, key):
        i = bisect.bisect_right(self.ring, h64(key)) % len(self.ring)
        return self.owner[self.ring[i]]


# ---------- 블룸 필터 ----------

class BloomFilter:
    """m비트 배열과 해시 k개. 추가: k개 위치를 1로. 조회: k개가 모두 1이면 '아마 있음', 하나라도 0이면 '확실히 없음'."""

    def __init__(self, m, k):
        self.m, self.k, self.bits = m, k, bytearray((m + 7) // 8)

    def _positions(self, item):
        d = hashlib.sha256(item.encode()).digest()
        a, b = int.from_bytes(d[:8], "big"), int.from_bytes(d[8:16], "big") | 1
        return [(a + i * b) % self.m for i in range(self.k)]   # 이중 해싱으로 해시 k개를 만든다

    def add(self, item):
        for p in self._positions(item): self.bits[p >> 3] |= 1 << (p & 7)

    def __contains__(self, item):
        return all(self.bits[p >> 3] >> (p & 7) & 1 for p in self._positions(item))


def optimal_bloom(n, fp):
    """원소 n개, 목표 거짓 양성률 fp일 때 m = -n ln fp / (ln 2)^2, k = (m/n) ln 2."""
    m = math.ceil(-n * math.log(fp) / math.log(2) ** 2)
    return m, max(1, round(m / n * math.log(2)))


# ---------- 스킵 리스트 ----------

class SkipNode:
    __slots__ = ("key", "next")
    def __init__(self, key, level):
        self.key, self.next = key, [None] * level


class SkipList:
    """정렬된 연결 리스트 위에 '급행 차선'을 확률적으로 쌓는다. 새 노드의 높이는 동전 던지기(p = 1/2)로 정한다.
    검색은 가장 높은 층에서 오른쪽으로 가다가 넘어설 것 같으면 한 층 내려간다. 기대 O(log n)."""
    MAX = 32

    def __init__(self, rng):
        self.head, self.level, self.rng, self.size = SkipNode(None, self.MAX), 1, rng, 0

    def _random_level(self):
        lv = 1
        while lv < self.MAX and self.rng.random() < 0.5: lv += 1
        return lv

    def _find_prev(self, key, steps=None):
        update, x = [None] * self.MAX, self.head
        for i in range(self.level - 1, -1, -1):
            while x.next[i] and x.next[i].key < key:
                x = x.next[i]
                if steps is not None: steps[0] += 1
            update[i] = x
        return update

    def search(self, key, steps=None):
        x = self._find_prev(key, steps)[0].next[0]
        return x is not None and x.key == key

    def insert(self, key):
        update = self._find_prev(key)
        if update[0].next[0] and update[0].next[0].key == key: return False
        lv = self._random_level()
        if lv > self.level:
            for i in range(self.level, lv): update[i] = self.head
            self.level = lv
        node = SkipNode(key, lv)
        for i in range(lv):
            node.next[i] = update[i].next[i]; update[i].next[i] = node
        self.size += 1
        return True

    def delete(self, key):
        update = self._find_prev(key)
        x = update[0].next[0]
        if not x or x.key != key: return False
        for i in range(len(x.next)):
            update[i].next[i] = x.next[i]
        while self.level > 1 and self.head.next[self.level - 1] is None: self.level -= 1
        self.size -= 1
        return True

    def keys(self):
        out, x = [], self.head.next[0]
        while x: out.append(x.key); x = x.next[0]
        return out


if __name__ == "__main__":
    rng = random.Random(52)
    keys = [f"user:{i}" for i in range(100000)]

    # 1) 서버 추가 시 이동하는 키 비율: 나머지 해싱 vs 일관된 해싱
    before = {k: h64(k) % 10 for k in keys}
    after = {k: h64(k) % 11 for k in keys}
    moved_mod = sum(before[k] != after[k] for k in keys) / len(keys)
    ch = ConsistentHash(vnodes=100)
    for s in range(10): ch.add(f"server{s}")
    b2 = {k: ch.get(k) for k in keys}
    ch.add("server10")
    a2 = {k: ch.get(k) for k in keys}
    moved_ch = sum(b2[k] != a2[k] for k in keys) / len(keys)
    assert all(a2[k] == "server10" for k in keys if b2[k] != a2[k])     # 옮겨진 키는 모두 새 서버로
    print(f"서버 10 → 11대: 나머지(hash % n) 방식은 키 {100 * moved_mod:.1f}% 이동, 일관된 해싱은 {100 * moved_ch:.1f}% 이동 (이상적 1/11 = 9.1%)")
    ch.remove("server10")
    assert all(ch.get(k) == b2[k] for k in keys)
    print("서버 제거 후: 모든 키가 추가 전 서버로 돌아감 (다른 서버의 키는 영향 없음)")

    # 2) 가상 노드 수에 따른 부하 균형
    for v in (1, 10, 100, 500):
        c = ConsistentHash(vnodes=v)
        for s in range(10): c.add(f"server{s}")
        load = {}
        for k in keys: load[c.get(k)] = load.get(c.get(k), 0) + 1
        vals = [load.get(f"server{s}", 0) for s in range(10)]
        print(f"가상 노드 {v:3d}개: 서버별 키 수 최소 {min(vals):,} / 최대 {max(vals):,} (평균 10,000), 표준편차 {statistics.pstdev(vals):,.0f}")

    # 3) 블룸 필터 거짓 양성률: 이론값과 측정값
    print()
    n = 10000
    for fp in (0.1, 0.01, 0.001):
        m, k = optimal_bloom(n, fp)
        bf = BloomFilter(m, k)
        for i in range(n): bf.add(f"in:{i}")
        assert all(f"in:{i}" in bf for i in range(n))                   # 거짓 음성은 없다
        trials = 200000
        fps = sum(f"out:{i}" in bf for i in range(trials)) / trials
        theory = (1 - math.exp(-k * n / m)) ** k
        print(f"원소 {n:,}개, 목표 {fp}: m = {m:,}비트({m / 8 / 1024:.1f}KB, 원소당 {m / n:.1f}비트), k = {k}, "
              f"이론 {theory:.4f}, 측정 {fps:.4f}")
    m, k = 95851, 7
    for extra in (1, 2, 4):
        bf = BloomFilter(m, k)
        for i in range(n * extra): bf.add(f"in:{i}")
        fps = sum(f"out:{i}" in bf for i in range(100000)) / 100000
        print(f"  같은 크기(m={m:,}, k={k})에 원소 {n * extra:,}개를 넣으면 측정 거짓 양성률 {fps:.4f}")

    # 4) 스킵 리스트: 정렬된 리스트(set + sorted)와 동작 비교
    print()
    for _ in range(200):
        sl, ref = SkipList(rng), set()
        for _ in range(300):
            x, op = rng.randint(0, 100), rng.random()
            if op < 0.5: assert sl.insert(x) == (x not in ref); ref.add(x)
            elif op < 0.8: assert sl.delete(x) == (x in ref); ref.discard(x)
            else: assert sl.search(x) == (x in ref)
        assert sl.keys() == sorted(ref) and sl.size == len(ref)
    print("스킵 리스트: 200개 × 300개 무작위 삽입·삭제·검색에서 정렬된 집합과 같은 결과")
    for n in (1000, 100000):
        sl = SkipList(rng)
        data = rng.sample(range(10 * n), n)
        for x in data: sl.insert(x)
        steps = [0]
        for x in rng.sample(data, 1000): sl.search(x, steps)
        hist = {}
        x = sl.head.next[0]
        while x: hist[len(x.next)] = hist.get(len(x.next), 0) + 1; x = x.next[0]
        print(f"원소 {n:,}개: 최고 층 {sl.level}, 검색 1회 평균 이동 {steps[0] / 1000:.1f}번 (log2 n = {math.log2(n):.1f}), "
              f"높이 1·2·3인 노드 비율 {hist.get(1, 0) / n:.2f}·{hist.get(2, 0) / n:.2f}·{hist.get(3, 0) / n:.2f}")
