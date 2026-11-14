"""인터프리터 패턴: 간단한 언어의 문법 규칙 하나하나를 클래스로 만들고, 구문 트리를 해석한다.

문법 (검색 필터 언어):
    expr   := term ("OR" term)*
    term   := factor ("AND" factor)*
    factor := "NOT" factor | "(" expr ")" | WORD

python interpreter.py 로 실행하면 무작위 검증과 예제 출력이 나온다.
"""
from abc import ABC, abstractmethod
import random
import re


class Expr(ABC):
    @abstractmethod
    def interpret(self, ctx: set[str]) -> bool: ...


class Word(Expr):                                 # 터미널 표현식
    def __init__(self, w): self.w = w
    def interpret(self, ctx): return self.w in ctx
    def __repr__(self): return self.w


class Not(Expr):                                  # 비터미널 표현식
    def __init__(self, e): self.e = e
    def interpret(self, ctx): return not self.e.interpret(ctx)
    def __repr__(self): return f"NOT({self.e})"


class And(Expr):
    def __init__(self, l, r): self.l, self.r = l, r
    def interpret(self, ctx): return self.l.interpret(ctx) and self.r.interpret(ctx)
    def __repr__(self): return f"AND({self.l}, {self.r})"


class Or(Expr):
    def __init__(self, l, r): self.l, self.r = l, r
    def interpret(self, ctx): return self.l.interpret(ctx) or self.r.interpret(ctx)
    def __repr__(self): return f"OR({self.l}, {self.r})"


# 파서: 문자열 -> 구문 트리 (재귀 하강). 패턴 자체는 파싱을 다루지 않지만 실사용에는 필요하다
class Parser:
    def __init__(self, text):
        self.toks = re.findall(r"\(|\)|[^\s()]+", text)
        self.i = 0

    def peek(self): return self.toks[self.i] if self.i < len(self.toks) else None

    def eat(self, t=None):
        tok = self.peek()
        if tok is None or (t and tok != t):
            raise SyntaxError(f"expected {t or 'WORD'}, got {tok or 'end of input'}")
        self.i += 1
        return tok

    def parse(self):
        e = self.expr()
        if self.peek() is not None:
            raise SyntaxError(f"unexpected {self.peek()}")
        return e

    def expr(self):
        e = self.term()
        while self.peek() == "OR":
            self.eat(); e = Or(e, self.term())
        return e

    def term(self):
        e = self.factor()
        while self.peek() == "AND":
            self.eat(); e = And(e, self.factor())
        return e

    def factor(self):
        tok = self.peek()
        if tok == "NOT":
            self.eat(); return Not(self.factor())
        if tok == "(":
            self.eat("("); e = self.expr(); self.eat(")"); return e
        return Word(self.eat())


def random_query(rng, words, depth=0):
    if depth > 3 or rng.random() < 0.3:
        return rng.choice(words)
    r = rng.random()
    if r < 0.2:
        return f"NOT {random_query(rng, words, depth + 1)}"
    op = "AND" if r < 0.6 else "OR"
    return f"( {random_query(rng, words, depth + 1)} {op} {random_query(rng, words, depth + 1)} )"


if __name__ == "__main__":
    q = "python AND (django OR flask) AND NOT legacy"
    tree = Parser(q).parse()
    print("구문 트리:", tree)
    posts = {
        "p1": {"python", "django"},
        "p2": {"python", "flask", "legacy"},
        "p3": {"java", "spring"},
        "p4": {"python", "flask"},
    }
    hits = [k for k, tags in posts.items() if tree.interpret(tags)]
    print("검색 결과:", hits)
    assert hits == ["p1", "p4"]

    # 무작위 검증: 같은 질의를 Python 불리언 식으로 바꿔 eval한 결과와 비교
    rng = random.Random(3)
    words = ["a", "b", "c", "d"]
    for _ in range(1000):
        q = random_query(rng, words)
        t = Parser(q).parse()
        ctx = {w for w in words if rng.random() < 0.5}
        py = q.replace("AND", "and").replace("OR", "or").replace("NOT", "not")
        expected = eval(py, {}, {w: (w in ctx) for w in words})
        assert t.interpret(ctx) == expected, q
    print("무작위 질의 1000개: Python 불리언 식 결과와 일치")

    try:
        Parser("a AND (b OR").parse()
    except SyntaxError as e:
        print("문법 오류:", e)
    print("모든 검증 통과")
