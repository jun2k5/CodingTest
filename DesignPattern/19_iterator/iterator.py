"""이터레이터 패턴: 컬렉션의 내부 구조를 드러내지 않고 원소를 차례로 꺼낸다.

python iterator.py 로 실행하면 무작위 검증과 예제 출력이 나온다.
"""
from collections import deque
import itertools
import random


class Node:
    def __init__(self, val, left=None, right=None):
        self.val, self.left, self.right = val, left, right


class BST:
    def __init__(self): self.root = None

    def insert(self, v):
        if self.root is None:
            self.root = Node(v); return
        cur = self.root
        while True:
            if v < cur.val:
                if cur.left is None: cur.left = Node(v); return
                cur = cur.left
            else:
                if cur.right is None: cur.right = Node(v); return
                cur = cur.right

    # 1. 고전 형태: 별도 이터레이터 클래스 (__iter__ + __next__)
    def __iter__(self):
        return InorderIterator(self.root)

    # 2. 제너레이터: 같은 순회를 함수 하나로
    def preorder(self):
        stack = [self.root] if self.root else []
        while stack:
            n = stack.pop()
            yield n.val
            if n.right: stack.append(n.right)
            if n.left: stack.append(n.left)

    def level_order(self):
        q = deque([self.root] if self.root else [])
        while q:
            n = q.popleft()
            yield n.val
            if n.left: q.append(n.left)
            if n.right: q.append(n.right)


class InorderIterator:
    """스택으로 중위 순회 상태를 들고 다닌다. 메모리는 O(트리 높이)."""
    def __init__(self, root):
        self.stack = []
        self._push_left(root)

    def _push_left(self, n):
        while n:
            self.stack.append(n)
            n = n.left

    def __iter__(self): return self

    def __next__(self):
        if not self.stack:
            raise StopIteration
        n = self.stack.pop()
        self._push_left(n.right)
        return n.val


def countdown(n):
    """무한·지연 시퀀스: 필요할 때만 값을 만든다."""
    while True:
        yield n
        n -= 1


if __name__ == "__main__":
    t = BST()
    for v in [50, 30, 70, 20, 40, 60, 80]:
        t.insert(v)
    print("중위:", list(t))
    print("전위:", list(t.preorder()))
    print("레벨:", list(t.level_order()))
    assert list(t) == [20, 30, 40, 50, 60, 70, 80]
    assert list(t.preorder()) == [50, 30, 20, 40, 70, 60, 80]
    assert list(t.level_order()) == [50, 30, 70, 20, 40, 60, 80]

    # 이터레이터 두 개는 서로 독립적인 위치를 가진다
    a, b = iter(t), iter(t)
    next(a); next(a)
    assert next(a) == 40 and next(b) == 20

    # 소비된 이터레이터는 다시 쓸 수 없다 (이터러블과 이터레이터의 차이)
    it = iter(t)
    assert list(it) and list(it) == []
    assert list(t) == list(t)                       # BST는 이터러블이라 매번 새 이터레이터

    print("지연 시퀀스 앞 5개:", list(itertools.islice(countdown(10), 5)))

    rng = random.Random(5)
    for _ in range(300):
        vals = [rng.randint(0, 100) for _ in range(rng.randint(0, 50))]
        t = BST()
        for v in vals: t.insert(v)
        assert list(t) == sorted(vals)
        assert sorted(t.preorder()) == sorted(vals) == sorted(t.level_order())
    print("무작위 트리 300개: 중위 순회 = sorted(), 세 순회 원소 집합 일치")
    print("모든 검증 통과")
