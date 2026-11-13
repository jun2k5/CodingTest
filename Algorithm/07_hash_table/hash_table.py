"""해시 테이블: 체이닝과 개방 주소법(선형 탐사), 동적 확장."""
import random


class ChainingHashMap:
    def __init__(self, cap=8):
        self.buckets = [[] for _ in range(cap)]
        self.size = 0

    def _idx(self, key):
        return hash(key) % len(self.buckets)

    def put(self, key, value):
        b = self.buckets[self._idx(key)]
        for i, (k, _) in enumerate(b):
            if k == key:
                b[i] = (key, value)
                return
        b.append((key, value))
        self.size += 1
        if self.size / len(self.buckets) > 0.75:      # 적재율이 높아지면 두 배로 늘리고 재배치
            self._resize(len(self.buckets) * 2)

    def get(self, key, default=None):
        for k, v in self.buckets[self._idx(key)]:
            if k == key:
                return v
        return default

    def remove(self, key):
        b = self.buckets[self._idx(key)]
        for i, (k, _) in enumerate(b):
            if k == key:
                b.pop(i)
                self.size -= 1
                return True
        return False

    def _resize(self, cap):
        old = [kv for b in self.buckets for kv in b]
        self.buckets = [[] for _ in range(cap)]
        self.size = 0
        for k, v in old:
            self.put(k, v)


_EMPTY, _DELETED = object(), object()


class LinearProbingHashMap:
    def __init__(self, cap=8):
        self.keys = [_EMPTY] * cap
        self.vals = [None] * cap
        self.size = 0
        self.probes = 0

    def _find(self, key):
        """key가 있는 칸, 없으면 넣을 칸(처음 만난 DELETED 우선)."""
        cap = len(self.keys)
        i = hash(key) % cap
        first_deleted = None
        for _ in range(cap):
            self.probes += 1
            k = self.keys[i]
            if k is _EMPTY:
                return (first_deleted if first_deleted is not None else i), False
            if k is _DELETED:
                if first_deleted is None:
                    first_deleted = i
            elif k == key:
                return i, True
            i = (i + 1) % cap                           # 다음 칸을 본다
        return first_deleted, False

    def put(self, key, value):
        if (self.size + 1) / len(self.keys) > 0.5:     # 개방 주소법은 적재율을 낮게 유지
            self._resize(len(self.keys) * 2)
        i, found = self._find(key)
        if not found:
            self.size += 1
        self.keys[i], self.vals[i] = key, value

    def get(self, key, default=None):
        i, found = self._find(key)
        return self.vals[i] if found else default

    def remove(self, key):
        i, found = self._find(key)
        if found:
            self.keys[i], self.vals[i] = _DELETED, None   # 빈칸으로 두면 뒤쪽 탐사가 끊긴다
            self.size -= 1
        return found

    def _resize(self, cap):
        old = [(k, v) for k, v in zip(self.keys, self.vals) if k is not _EMPTY and k is not _DELETED]
        self.keys, self.vals, self.size = [_EMPTY] * cap, [None] * cap, 0
        for k, v in old:
            self.put(k, v)


if __name__ == "__main__":
    rng = random.Random(13)
    for cls in (ChainingHashMap, LinearProbingHashMap):
        for _ in range(200):
            h, ref = cls(), {}
            for _ in range(rng.randint(1, 300)):
                k = rng.randint(0, 60)
                r = rng.random()
                if r < 0.5:
                    v = rng.random(); h.put(k, v); ref[k] = v
                elif r < 0.8:
                    assert h.get(k) == ref.get(k)
                else:
                    assert h.remove(k) == (k in ref); ref.pop(k, None)
            assert h.size == len(ref)
        print(f"{cls.__name__}: dict와 200개 무작위 시나리오 일치")

    # 같은 버킷 수에서 키 패턴에 따른 충돌: 버킷 수가 키 간격과 공약수를 가지면 몰린다
    for cap in (16, 17):
        b = [0] * cap
        for key in range(0, 16 * 50, 16):
            b[key % cap] += 1
        print(f"버킷 {cap}개, 16의 배수 키 50개: 사용한 버킷 {sum(1 for c in b if c)}개, 최대 {max(b)}개")

    h = LinearProbingHashMap(cap=8)
    for k in [1, 9, 17]:
        h.put(k, k)
    h.remove(9)
    print("선형 탐사: 1, 9, 17 넣고 9 삭제 후 get(17) =", h.get(17), "(삭제 표시 덕분에 탐사가 끊기지 않음)")
