"""AVL 트리: 높이 균형 이진 탐색 트리 (삽입·삭제와 4가지 회전)."""
import random


class Node:
    __slots__ = ("key", "left", "right", "h")

    def __init__(self, key):
        self.key, self.left, self.right, self.h = key, None, None, 1


def h(n):
    return n.h if n else 0


def update(n):
    n.h = 1 + max(h(n.left), h(n.right))


def balance(n):
    return h(n.left) - h(n.right)


def rotate_right(y):
    x = y.left
    y.left, x.right = x.right, y
    update(y); update(x)
    return x


def rotate_left(x):
    y = x.right
    x.right, y.left = y.left, x
    update(x); update(y)
    return y


ROTATIONS = {"LL": 0, "RR": 0, "LR": 0, "RL": 0}


def rebalance(n):
    update(n)
    b = balance(n)
    if b > 1:                                   # 왼쪽이 높다
        if balance(n.left) < 0:                 # LR: 왼쪽 자식을 먼저 왼쪽 회전
            ROTATIONS["LR"] += 1
            n.left = rotate_left(n.left)
        else:
            ROTATIONS["LL"] += 1
        return rotate_right(n)
    if b < -1:                                  # 오른쪽이 높다
        if balance(n.right) > 0:                # RL
            ROTATIONS["RL"] += 1
            n.right = rotate_right(n.right)
        else:
            ROTATIONS["RR"] += 1
        return rotate_left(n)
    return n


def insert(n, key):
    if n is None:
        return Node(key)
    if key < n.key:
        n.left = insert(n.left, key)
    elif key > n.key:
        n.right = insert(n.right, key)
    else:
        return n
    return rebalance(n)


def delete(n, key):
    if n is None:
        return None
    if key < n.key:
        n.left = delete(n.left, key)
    elif key > n.key:
        n.right = delete(n.right, key)
    else:
        if n.left is None or n.right is None:
            return n.left or n.right
        s = n.right
        while s.left:
            s = s.left
        n.key = s.key
        n.right = delete(n.right, s.key)
    return rebalance(n)


def inorder(n, out):
    if n: inorder(n.left, out); out.append(n.key); inorder(n.right, out)
    return out


def check(n):
    """모든 노드의 균형 인수가 -1..1이고 높이가 맞는지 검사."""
    if n is None:
        return 0
    lh, rh = check(n.left), check(n.right)
    assert abs(lh - rh) <= 1 and n.h == 1 + max(lh, rh)
    return n.h


if __name__ == "__main__":
    rng = random.Random(19)
    for _ in range(300):
        root, ref = None, set()
        for _ in range(rng.randint(1, 200)):
            k = rng.randint(0, 80)
            if rng.random() < 0.6:
                root = insert(root, k); ref.add(k)
            else:
                root = delete(root, k); ref.discard(k)
            check(root)
        assert inorder(root, []) == sorted(ref)
    print("AVL: 300개 무작위 시나리오에서 균형 조건과 정렬 순서 유지")

    for k in ROTATIONS: ROTATIONS[k] = 0
    root = None
    for k in [30, 20, 10]:
        root = insert(root, k)
    print("30, 20, 10 삽입(LL) -> 루트", root.key, "회전", {k: v for k, v in ROTATIONS.items() if v})
    for k in ROTATIONS: ROTATIONS[k] = 0
    root = None
    for k in [30, 10, 20]:
        root = insert(root, k)
    print("30, 10, 20 삽입(LR) -> 루트", root.key, "회전", {k: v for k, v in ROTATIONS.items() if v})

    root = None
    for k in range(1000):
        root = insert(root, k)
    print("정렬된 순서로 1000개 삽입한 높이:", root.h, "(BST는 1000)")
