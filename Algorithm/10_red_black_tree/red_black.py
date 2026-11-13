"""레드-블랙 트리 (CLRS 방식): 삽입·삭제와 5가지 성질 검사."""
import random

RED, BLACK = 0, 1


class Node:
    __slots__ = ("key", "color", "left", "right", "parent")

    def __init__(self, key, color=RED, nil=None):
        self.key, self.color = key, color
        self.left = self.right = self.parent = nil


class RBTree:
    def __init__(self):
        self.NIL = Node(None, BLACK)            # 모든 잎을 대신하는 검은 경계 노드
        self.root = self.NIL

    def _rotate_left(self, x):
        y = x.right
        x.right = y.left
        if y.left is not self.NIL: y.left.parent = x
        y.parent = x.parent
        if x.parent is self.NIL: self.root = y
        elif x is x.parent.left: x.parent.left = y
        else: x.parent.right = y
        y.left, x.parent = x, y

    def _rotate_right(self, x):
        y = x.left
        x.left = y.right
        if y.right is not self.NIL: y.right.parent = x
        y.parent = x.parent
        if x.parent is self.NIL: self.root = y
        elif x is x.parent.right: x.parent.right = y
        else: x.parent.left = y
        y.right, x.parent = x, y

    def search(self, key):
        n = self.root
        while n is not self.NIL and n.key != key:
            n = n.left if key < n.key else n.right
        return n

    def insert(self, key):
        parent, cur = self.NIL, self.root
        while cur is not self.NIL:
            parent = cur
            if key == cur.key: return
            cur = cur.left if key < cur.key else cur.right
        z = Node(key, RED, self.NIL)
        z.parent = parent
        if parent is self.NIL: self.root = z
        elif key < parent.key: parent.left = z
        else: parent.right = z
        self._insert_fix(z)

    def _insert_fix(self, z):
        while z.parent.color == RED:             # 빨강-빨강 연속을 없앤다
            gp = z.parent.parent
            if z.parent is gp.left:
                uncle = gp.right
                if uncle.color == RED:           # 경우 1: 삼촌이 빨강 → 색만 바꾸고 위로
                    z.parent.color = uncle.color = BLACK
                    gp.color = RED
                    z = gp
                else:
                    if z is z.parent.right:      # 경우 2: 꺾인 모양 → 회전해 경우 3으로
                        z = z.parent
                        self._rotate_left(z)
                    z.parent.color = BLACK       # 경우 3: 일직선 → 할아버지 기준 회전
                    gp.color = RED
                    self._rotate_right(gp)
            else:
                uncle = gp.left
                if uncle.color == RED:
                    z.parent.color = uncle.color = BLACK
                    gp.color = RED
                    z = gp
                else:
                    if z is z.parent.left:
                        z = z.parent
                        self._rotate_right(z)
                    z.parent.color = BLACK
                    gp.color = RED
                    self._rotate_left(gp)
        self.root.color = BLACK

    def _transplant(self, u, v):
        if u.parent is self.NIL: self.root = v
        elif u is u.parent.left: u.parent.left = v
        else: u.parent.right = v
        v.parent = u.parent

    def delete(self, key):
        z = self.search(key)
        if z is self.NIL: return
        y, y_color = z, z.color
        if z.left is self.NIL:
            x = z.right; self._transplant(z, z.right)
        elif z.right is self.NIL:
            x = z.left; self._transplant(z, z.left)
        else:
            y = z.right
            while y.left is not self.NIL: y = y.left
            y_color, x = y.color, y.right
            if y.parent is z:
                x.parent = y
            else:
                self._transplant(y, y.right)
                y.right = z.right; y.right.parent = y
            self._transplant(z, y)
            y.left = z.left; y.left.parent = y
            y.color = z.color
        if y_color == BLACK:                      # 검은 노드가 빠지면 검은 높이를 맞춘다
            self._delete_fix(x)

    def _delete_fix(self, x):
        while x is not self.root and x.color == BLACK:
            if x is x.parent.left:
                w = x.parent.right
                if w.color == RED:
                    w.color, x.parent.color = BLACK, RED
                    self._rotate_left(x.parent); w = x.parent.right
                if w.left.color == BLACK and w.right.color == BLACK:
                    w.color = RED; x = x.parent
                else:
                    if w.right.color == BLACK:
                        w.left.color, w.color = BLACK, RED
                        self._rotate_right(w); w = x.parent.right
                    w.color, x.parent.color, w.right.color = x.parent.color, BLACK, BLACK
                    self._rotate_left(x.parent); x = self.root
            else:
                w = x.parent.left
                if w.color == RED:
                    w.color, x.parent.color = BLACK, RED
                    self._rotate_right(x.parent); w = x.parent.left
                if w.right.color == BLACK and w.left.color == BLACK:
                    w.color = RED; x = x.parent
                else:
                    if w.left.color == BLACK:
                        w.right.color, w.color = BLACK, RED
                        self._rotate_left(w); w = x.parent.left
                    w.color, x.parent.color, w.left.color = x.parent.color, BLACK, BLACK
                    self._rotate_right(x.parent); x = self.root
        x.color = BLACK

    def inorder(self):
        out, stack, n = [], [], self.root
        while stack or n is not self.NIL:
            while n is not self.NIL: stack.append(n); n = n.left
            n = stack.pop(); out.append(n.key); n = n.right
        return out

    def check(self):
        """성질 2(루트 검정), 4(빨강의 자식은 검정), 5(검은 높이 동일) 검사. 높이도 반환."""
        assert self.root.color == BLACK
        def go(n):
            if n is self.NIL: return 1, 0
            if n.color == RED:
                assert n.left.color == BLACK and n.right.color == BLACK
            lb, lh = go(n.left); rb, rh = go(n.right)
            assert lb == rb
            return lb + (n.color == BLACK), 1 + max(lh, rh)
        return go(self.root)


if __name__ == "__main__":
    rng = random.Random(23)
    for _ in range(300):
        t, ref = RBTree(), set()
        for _ in range(rng.randint(1, 200)):
            k = rng.randint(0, 80)
            if rng.random() < 0.6:
                t.insert(k); ref.add(k)
            else:
                t.delete(k); ref.discard(k)
            t.check()
        assert t.inorder() == sorted(ref)
    print("레드-블랙 트리: 300개 무작위 시나리오에서 성질 유지, 정렬 순서 일치")
    t = RBTree()
    for k in range(1000): t.insert(k)
    bh, height = t.check()
    print(f"정렬된 순서로 1000개 삽입: 높이 {height}, 검은 높이 {bh} (상한 2·log2(1001) ≈ 19.9)")
