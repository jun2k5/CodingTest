"""B-트리(최소 차수 t)의 탐색·삽입(분할)과 B+트리 범위 검색 비교."""
import bisect, random


class BNode:
    def __init__(self, leaf=True):
        self.keys, self.children, self.leaf = [], [], leaf


class BTree:
    """각 노드는 키 t-1 ~ 2t-1개(루트 제외), 자식은 키 수 + 1개."""

    def __init__(self, t=3):
        self.t, self.root = t, BNode()
        self.node_reads = 0

    def search(self, key, node=None):
        node = node or self.root
        self.node_reads += 1                         # 노드 하나 = 디스크 블록 하나를 읽는 비용
        i = bisect.bisect_left(node.keys, key)
        if i < len(node.keys) and node.keys[i] == key:
            return True
        if node.leaf:
            return False
        return self.search(key, node.children[i])

    def insert(self, key):
        if self.search(key):
            return
        r = self.root
        if len(r.keys) == 2 * self.t - 1:            # 루트가 꽉 차면 분할해 높이가 1 늘어난다
            s = BNode(leaf=False)
            s.children.append(r)
            self._split(s, 0)
            self.root = s
        self._insert_nonfull(self.root, key)

    def _split(self, parent, i):
        t, full = self.t, parent.children[i]
        right = BNode(full.leaf)
        mid = full.keys[t - 1]                        # 가운데 키를 부모로 올린다
        right.keys = full.keys[t:]
        full.keys = full.keys[:t - 1]
        if not full.leaf:
            right.children = full.children[t:]
            full.children = full.children[:t]
        parent.keys.insert(i, mid)
        parent.children.insert(i + 1, right)

    def _insert_nonfull(self, node, key):
        while not node.leaf:
            i = bisect.bisect_left(node.keys, key)
            if len(node.children[i].keys) == 2 * self.t - 1:   # 내려가기 전에 미리 분할
                self._split(node, i)
                if key > node.keys[i]:
                    i += 1
            node = node.children[i]
        bisect.insort(node.keys, key)

    def height(self):
        h, n = 1, self.root
        while not n.leaf:
            n, h = n.children[0], h + 1
        return h

    def inorder(self, node=None, out=None):
        node, out = node or self.root, [] if out is None else out
        for i, k in enumerate(node.keys):
            if not node.leaf: self.inorder(node.children[i], out)
            out.append(k)
        if not node.leaf: self.inorder(node.children[-1], out)
        return out

    def check(self, node=None, depth=0, leaf_depths=None):
        node = node or self.root
        leaf_depths = set() if leaf_depths is None else leaf_depths
        assert node.keys == sorted(node.keys) and len(node.keys) <= 2 * self.t - 1
        if node is not self.root: assert len(node.keys) >= self.t - 1
        if node.leaf: leaf_depths.add(depth)
        else:
            assert len(node.children) == len(node.keys) + 1
            for c in node.children: self.check(c, depth + 1, leaf_depths)
        assert len(leaf_depths) == 1                 # 모든 잎의 깊이가 같다
        return True


def bplus_range(leaves, lo, hi):
    """B+트리 잎 연결 리스트를 흉내: 정렬된 잎 블록 목록에서 범위를 순서대로 읽는다."""
    out, blocks = [], 0
    start = bisect.bisect_left([b[-1] for b in leaves], lo)
    for b in leaves[start:]:
        blocks += 1
        for k in b:
            if k > hi: return out, blocks
            if k >= lo: out.append(k)
    return out, blocks


if __name__ == "__main__":
    rng = random.Random(29)
    for t in (2, 3, 5):
        for _ in range(100):
            tree, ref = BTree(t), set()
            for _ in range(rng.randint(1, 300)):
                k = rng.randint(0, 500); tree.insert(k); ref.add(k)
            tree.check()
            assert tree.inorder() == sorted(ref)
            for q in range(0, 501, 7): assert tree.search(q) == (q in ref)
    print("B-트리(t=2,3,5): 300개 무작위 시나리오에서 균형·정렬·탐색 일치")

    for t in (2, 50, 100):
        tree = BTree(t)
        for k in range(100_000): tree.insert(k)
        tree.node_reads = 0; tree.search(77_777)
        print(f"t={t:3d} 키 10만 개: 높이 {tree.height()}, 키 하나 찾는 데 읽은 노드 {tree.node_reads}개")

    keys = list(range(0, 2000, 2))
    leaves = [keys[i:i + 100] for i in range(0, len(keys), 100)]
    res, blocks = bplus_range(leaves, 500, 900)
    print(f"B+트리 잎 연결로 범위 [500, 900] 읽기: 키 {len(res)}개, 잎 블록 {blocks}개")
