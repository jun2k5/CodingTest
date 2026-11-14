"""방문자 패턴: 객체 구조는 그대로 두고, 구조 위에서 수행할 새 연산을 별도 클래스로 추가한다.

python visitor.py 로 실행하면 무작위 검증과 예제 출력이 나온다.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from functools import singledispatch
import ast
import random


# 원소 계층 (수식 트리) -------------------------------------------------------
class Node(ABC):
    @abstractmethod
    def accept(self, v: Visitor): ...


class Num(Node):
    def __init__(self, value): self.value = value
    def accept(self, v): return v.visit_num(self)     # 이중 디스패치 1단계: 원소 타입으로 메서드 선택


class Add(Node):
    def __init__(self, l, r): self.l, self.r = l, r
    def accept(self, v): return v.visit_add(self)


class Mul(Node):
    def __init__(self, l, r): self.l, self.r = l, r
    def accept(self, v): return v.visit_mul(self)


# 방문자 계층: 연산 하나 = 클래스 하나 -------------------------------------------
class Visitor(ABC):
    @abstractmethod
    def visit_num(self, n: Num): ...
    @abstractmethod
    def visit_add(self, n: Add): ...
    @abstractmethod
    def visit_mul(self, n: Mul): ...


class Evaluate(Visitor):
    def visit_num(self, n): return n.value
    def visit_add(self, n): return n.l.accept(self) + n.r.accept(self)
    def visit_mul(self, n): return n.l.accept(self) * n.r.accept(self)


class Show(Visitor):
    def visit_num(self, n): return str(n.value)
    def visit_add(self, n): return f"({n.l.accept(self)} + {n.r.accept(self)})"
    def visit_mul(self, n): return f"{n.l.accept(self)} * {n.r.accept(self)}"


class CountNodes(Visitor):
    def visit_num(self, n): return 1
    def visit_add(self, n): return 1 + n.l.accept(self) + n.r.accept(self)
    def visit_mul(self, n): return 1 + n.l.accept(self) + n.r.accept(self)


# Python다운 대안: functools.singledispatch (원소 클래스에 accept가 필요 없다)
@singledispatch
def depth(n) -> int:
    raise TypeError(type(n))


@depth.register
def _(n: Num): return 1


@depth.register(Add)
@depth.register(Mul)
def _(n): return 1 + max(depth(n.l), depth(n.r))


# 표준 라이브러리의 방문자: ast.NodeVisitor (visit_<클래스 이름> 메서드로 분기)
class CallCounter(ast.NodeVisitor):
    def __init__(self): self.calls = []
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.calls.append(node.func.id)
        self.generic_visit(node)                       # 자식 노드도 계속 방문


def random_tree(rng, d=0):
    if d > 4 or rng.random() < 0.3:
        return Num(rng.randint(0, 9))
    return (Add if rng.random() < 0.5 else Mul)(random_tree(rng, d + 1), random_tree(rng, d + 1))


if __name__ == "__main__":
    tree = Mul(Add(Num(2), Num(3)), Num(4))
    print("Show      :", tree.accept(Show()))
    print("Evaluate  :", tree.accept(Evaluate()))
    print("CountNodes:", tree.accept(CountNodes()))
    print("depth     :", depth(tree))
    assert tree.accept(Evaluate()) == 20 and tree.accept(CountNodes()) == 5 and depth(tree) == 3

    rng = random.Random(9)
    for _ in range(1000):
        t = random_tree(rng)
        assert t.accept(Evaluate()) == eval(t.accept(Show()))     # 출력한 식을 Python이 계산한 값과 같다
    print("무작위 트리 1000개: Evaluate 결과 = Show 문자열을 eval한 값")

    src = "def f(x):\n    print(len(x))\n    return sorted(map(abs, x))\n"
    cc = CallCounter()
    cc.visit(ast.parse(src))
    print("ast.NodeVisitor로 찾은 함수 호출:", cc.calls)
    assert cc.calls == ["print", "len", "sorted", "map"]
    print("모든 검증 통과")
