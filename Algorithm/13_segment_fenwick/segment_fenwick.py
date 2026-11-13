"""세그먼트 트리(구간 합, 지연 전파 포함)와 펜윅 트리."""
import random


class SegmentTree:
    """점 갱신 + 구간 합. 반복문(bottom-up) 구현, 크기 2n."""

    def __init__(self, a):
        self.n = len(a)
        self.t = [0] * self.n + list(a)
        for i in range(self.n - 1, 0, -1):
            self.t[i] = self.t[2 * i] + self.t[2 * i + 1]

    def update(self, i, value):
        i += self.n
        self.t[i] = value
        while i > 1:
            i //= 2
            self.t[i] = self.t[2 * i] + self.t[2 * i + 1]

    def query(self, l, r):
        """구간 [l, r) 합."""
        res, l, r = 0, l + self.n, r + self.n
        while l < r:
            if l & 1: res += self.t[l]; l += 1
            if r & 1: r -= 1; res += self.t[r]
            l //= 2; r //= 2
        return res


class LazySegmentTree:
    """구간 더하기 + 구간 합. 재귀 구현, 지연 값은 자식으로 미뤄 둔다."""

    def __init__(self, a):
        self.n = len(a)
        self.t = [0] * (4 * self.n)
        self.lz = [0] * (4 * self.n)
        if self.n: self._build(a, 1, 0, self.n - 1)

    def _build(self, a, node, s, e):
        if s == e:
            self.t[node] = a[s]; return
        m = (s + e) // 2
        self._build(a, 2 * node, s, m); self._build(a, 2 * node + 1, m + 1, e)
        self.t[node] = self.t[2 * node] + self.t[2 * node + 1]

    def _push(self, node, s, e):
        if self.lz[node]:
            self.t[node] += self.lz[node] * (e - s + 1)
            if s != e:
                self.lz[2 * node] += self.lz[node]
                self.lz[2 * node + 1] += self.lz[node]
            self.lz[node] = 0

    def add(self, l, r, v, node=1, s=0, e=None):
        """[l, r] 구간에 v를 더한다."""
        e = self.n - 1 if e is None else e
        self._push(node, s, e)
        if r < s or e < l: return
        if l <= s and e <= r:
            self.lz[node] += v; self._push(node, s, e); return
        m = (s + e) // 2
        self.add(l, r, v, 2 * node, s, m); self.add(l, r, v, 2 * node + 1, m + 1, e)
        self.t[node] = self.t[2 * node] + self.t[2 * node + 1]

    def query(self, l, r, node=1, s=0, e=None):
        """[l, r] 구간 합."""
        e = self.n - 1 if e is None else e
        self._push(node, s, e)
        if r < s or e < l: return 0
        if l <= s and e <= r: return self.t[node]
        m = (s + e) // 2
        return self.query(l, r, 2 * node, s, m) + self.query(l, r, 2 * node + 1, m + 1, e)


class Fenwick:
    """1-indexed. i & -i 는 i의 가장 낮은 1 비트."""

    def __init__(self, n):
        self.n, self.t = n, [0] * (n + 1)

    def add(self, i, v):
        while i <= self.n:
            self.t[i] += v; i += i & -i

    def prefix(self, i):
        s = 0
        while i > 0:
            s += self.t[i]; i -= i & -i
        return s

    def range_sum(self, l, r):
        return self.prefix(r) - self.prefix(l - 1)


if __name__ == "__main__":
    rng = random.Random(37)
    for _ in range(200):
        n = rng.randint(1, 60)
        a = [rng.randint(-20, 20) for _ in range(n)]
        st, lz, fw = SegmentTree(a), LazySegmentTree(a), Fenwick(n)
        for i, v in enumerate(a): fw.add(i + 1, v)
        ref = a[:]
        for _ in range(100):
            l = rng.randrange(n); r = rng.randrange(l, n)
            op = rng.random()
            if op < 0.3:
                v = rng.randint(-20, 20)
                fw.add(l + 1, v - ref[l]); st.update(l, v)
                lz.add(l, l, v - ref[l]); ref[l] = v
            elif op < 0.5:
                v = rng.randint(-5, 5); lz.add(l, r, v)
                for i in range(l, r + 1):
                    st.update(i, ref[i] + v); fw.add(i + 1, v); ref[i] += v
            else:
                s = sum(ref[l:r + 1])
                assert st.query(l, r + 1) == lz.query(l, r) == fw.range_sum(l + 1, r + 1) == s
    print("세그먼트 트리·지연 세그먼트 트리·펜윅 트리: 200개 시나리오에서 단순 합과 일치")
    print("i & -i 예시:", [(i, i & -i) for i in [1, 2, 3, 4, 6, 8, 12]])
