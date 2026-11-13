"""이진 탐색 트리(삽입·탐색·삭제)와 네 가지 순회."""
import random
from collections import deque


class Node:
    __slots__ = ("key", "left", "right")

    def __init__(self, key):
        self.key, self.left, self.right = key, None, None


class BST:
    def __init__(self):
        self.root = None

    def insert(self, key):
        if self.root is None:
            self.root = Node(key); return True
        cur = self.root
        while True:
            if key == cur.key:
                return False                      # 중복은 넣지 않는다
            nxt = "left" if key < cur.key else "right"
            if getattr(cur, nxt) is None:
                setattr(cur, nxt, Node(key)); return True
            cur = getattr(cur, nxt)

    def search(self, key):
        cur = self.root
        while cur and cur.key != key:
            cur = cur.left if key < cur.key else cur.right
        return cur is not None

    def delete(self, key):
        self.root = self._delete(self.root, key)

    def _delete(self, node, key):
        if node is None:
            return None
        if key < node.key:
            node.left = self._delete(node.left, key)
        elif key > node.key:
            node.right = self._delete(node.right, key)
        else:
            if node.left is None:                 # 자식이 0개 또는 1개
                return node.right
            if node.right is None:
                return node.left
            succ = node.right                     # 자식이 2개: 오른쪽 서브트리의 최솟값(후속자)
            while succ.left:
                succ = succ.left
            node.key = succ.key
            node.right = self._delete(node.right, succ.key)
        return node

    def height(self, node="root"):
        node = self.root if node == "root" else node
        if node is None:
            return 0
        best, q = 0, deque([(node, 1)])
        while q:
            n, d = q.popleft(); best = max(best, d)
            if n.left: q.append((n.left, d + 1))
            if n.right: q.append((n.right, d + 1))
        return best


def preorder(n, out):
    if n: out.append(n.key); preorder(n.left, out); preorder(n.right, out)
    return out


def inorder(n, out):
    if n: inorder(n.left, out); out.append(n.key); inorder(n.right, out)
    return out


def postorder(n, out):
    if n: postorder(n.left, out); postorder(n.right, out); out.append(n.key)
    return out


def levelorder(root):
    out, q = [], deque([root] if root else [])
    while q:
        n = q.popleft(); out.append(n.key)
        if n.left: q.append(n.left)
        if n.right: q.append(n.right)
    return out


def inorder_iterative(root):
    out, stack, cur = [], [], root
    while stack or cur:
        while cur:
            stack.append(cur); cur = cur.left
        cur = stack.pop(); out.append(cur.key)
        cur = cur.right
    return out


if __name__ == "__main__":
    rng = random.Random(17)
    for _ in range(300):
        t, ref = BST(), set()
        for _ in range(rng.randint(1, 120)):
            k = rng.randint(0, 50)
            if rng.random() < 0.6:
                assert t.insert(k) == (k not in ref); ref.add(k)
            else:
                t.delete(k); ref.discard(k)
            assert t.search(k) == (k in ref)
        assert inorder(t.root, []) == sorted(ref) == inorder_iterative(t.root)
    print("BST: set과 300개 무작위 시나리오 일치, 중위 순회 = 정렬 결과")

    t = BST()
    for k in [8, 3, 10, 1, 6, 14, 4, 7, 13]:
        t.insert(k)
    print("전위", preorder(t.root, []))
    print("중위", inorder(t.root, []))
    print("후위", postorder(t.root, []))
    print("레벨", levelorder(t.root))
    t.delete(3)
    print("3 삭제 후 중위", inorder(t.root, []), " 루트의 왼쪽 =", t.root.left.key)

    s, r = BST(), BST()
    for k in range(1000): s.insert(k)
    keys = list(range(1000)); rng.shuffle(keys)
    for k in keys: r.insert(k)
    print("정렬된 순서로 1000개 삽입한 높이:", s.height(), " 무작위 순서:", r.height())
