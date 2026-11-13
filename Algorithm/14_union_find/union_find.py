"""유니온 파인드(서로소 집합): 경로 압축 + 랭크(크기) 합치기."""
import random


class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n
        self.sets = n

    def find(self, x):
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:            # 경로 압축: 지나온 노드를 모두 루트에 바로 붙인다
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False                        # 이미 같은 집합 → 그래프라면 사이클
        if self.size[ra] < self.size[rb]:       # 작은 트리를 큰 트리 밑에 붙인다
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]
        self.sets -= 1
        return True


class NaiveUnionFind:
    """최적화 없는 버전 (높이 비교용)."""

    def __init__(self, n):
        self.parent = list(range(n))

    def find(self, x):
        while self.parent[x] != x:
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[ra] = rb


def depth(parent, x):
    d = 0
    while parent[x] != x:
        x, d = parent[x], d + 1
    return d


if __name__ == "__main__":
    rng = random.Random(41)
    for _ in range(300):
        n = rng.randint(1, 40)
        uf, label = UnionFind(n), list(range(n))
        for _ in range(rng.randint(0, 80)):
            a, b = rng.randrange(n), rng.randrange(n)
            merged = uf.union(a, b)
            assert merged == (label[a] != label[b])
            if merged:
                old, new = label[b], label[a]
                label = [new if l == old else l for l in label]
            x, y = rng.randrange(n), rng.randrange(n)
            assert (uf.find(x) == uf.find(y)) == (label[x] == label[y])
        assert uf.sets == len(set(label))
    print("UnionFind: 300개 무작위 시나리오에서 집합 라벨링과 일치")

    n = 2000
    naive, uf = NaiveUnionFind(n), UnionFind(n)
    for i in range(n - 1):
        naive.union(i, i + 1); uf.union(i, i + 1)
    print(f"0-1, 1-2, ... 순서로 {n}개 합친 뒤 최대 깊이: 최적화 없음 {max(depth(naive.parent, i) for i in range(n))}, "
          f"크기 합치기+경로 압축 {max(depth(uf.parent, i) for i in range(n))}")

    edges = [(1, 2), (2, 3), (3, 1), (4, 5)]
    u = UnionFind(6)
    print("간선 (1,2) (2,3) (3,1) (4,5): 사이클을 만드는 간선 =", [e for e in edges if not u.union(*e)])
