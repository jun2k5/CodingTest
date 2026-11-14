"""컴포지트 패턴: 개별 객체와 객체 묶음을 같은 인터페이스로 다룬다 (트리 구조).

python composite.py 로 실행하면 검증과 예제 출력이 나온다.
"""
from abc import ABC, abstractmethod
import random


class Node(ABC):                                   # Component
    def __init__(self, name: str): self.name = name

    @abstractmethod
    def size(self) -> int: ...

    @abstractmethod
    def render(self, depth=0) -> list[str]: ...


class File(Node):                                  # Leaf
    def __init__(self, name, size):
        super().__init__(name)
        self._size = size

    def size(self): return self._size

    def render(self, depth=0):
        return ["  " * depth + f"{self.name} ({self._size})"]


class Folder(Node):                                # Composite
    def __init__(self, name, children=None):
        super().__init__(name)
        self.children: list[Node] = list(children or [])

    def add(self, node: Node):
        self.children.append(node)
        return self

    def remove(self, node: Node):
        self.children.remove(node)

    def size(self):
        return sum(c.size() for c in self.children)   # 자식이 파일이든 폴더든 같은 호출

    def render(self, depth=0):
        lines = ["  " * depth + f"{self.name}/ ({self.size()})"]
        for c in self.children:
            lines += c.render(depth + 1)
        return lines


def find(node: Node, pred) -> list[str]:
    """트리 전체에서 조건에 맞는 파일 이름을 찾는다. 클라이언트는 Leaf/Composite를 구분하지 않는다."""
    out = []
    if isinstance(node, Folder):
        for c in node.children:
            out += find(c, pred)
    elif pred(node):
        out.append(node.name)
    return out


def random_tree(rng, depth=0):
    if depth >= 3 or rng.random() < 0.3:
        s = rng.randint(1, 100)
        return File(f"f{rng.randint(0, 999)}", s), s
    folder, total = Folder(f"d{depth}"), 0
    for _ in range(rng.randint(0, 4)):
        child, s = random_tree(rng, depth + 1)
        folder.add(child)
        total += s
    return folder, total


if __name__ == "__main__":
    root = Folder("project", [
        File("README.md", 3),
        Folder("src", [File("main.py", 12), File("util.py", 7), Folder("api", [File("views.py", 20)])]),
        Folder("docs", []),
    ])
    print("\n".join(root.render()))
    assert root.size() == 42
    assert find(root, lambda f: f.name.endswith(".py")) == ["main.py", "util.py", "views.py"]

    rng = random.Random(1)
    for _ in range(500):
        t, expected = random_tree(rng)
        assert t.size() == expected
    print("무작위 트리 500개: size()가 직접 더한 값과 일치")
    print("모든 검증 통과")
