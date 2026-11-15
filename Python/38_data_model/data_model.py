"""38. 데이터 모델과 매직 메서드: repr/str, eq/hash 계약, 연산자와 NotImplemented, 컨테이너 프로토콜, bool, call"""
import math


class Vector:
    __match_args__ = ("x", "y")

    def __init__(self, x, y):
        self.x, self.y = x, y

    def __repr__(self):                      # 개발자용: 다시 만들 수 있는 형태
        return f"Vector({self.x!r}, {self.y!r})"

    def __str__(self):                       # 사용자용
        return f"({self.x}, {self.y})"

    def __eq__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)

    def __hash__(self):                      # __eq__와 같은 필드로
        return hash((self.x, self.y))

    def __add__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        return Vector(self.x + other.x, self.y + other.y)

    def __mul__(self, k):
        if not isinstance(k, (int, float)):
            return NotImplemented
        return Vector(self.x * k, self.y * k)

    __rmul__ = __mul__                       # 3 * v도 되게

    def __abs__(self):
        return math.hypot(self.x, self.y)

    def __bool__(self):
        return bool(self.x or self.y)


def basics():
    v = Vector(3, 4)
    print("repr:", repr(v), "| str:", str(v), "| f-string:", f"{v}", f"{v!r}")
    print("연산자:", v + Vector(1, 1), v * 2, 3 * v, abs(v))
    print("bool:", bool(Vector(0, 0)), bool(v))
    print("집합·딕셔너리 키:", {Vector(1, 2), Vector(1, 2)}, {v: "a"}[Vector(3, 4)])
    try:
        v + 1
    except TypeError as e:
        print("NotImplemented → TypeError:", e)


class OnlyEq:
    def __init__(self, v):
        self.v = v

    def __eq__(self, other):
        return isinstance(other, OnlyEq) and self.v == other.v


class MutableBadHash:
    def __init__(self, v):
        self.v = v

    def __eq__(self, other):
        return self.v == other.v

    def __hash__(self):
        return hash(self.v)


def eq_hash_contract():
    print("__eq__만 정의하면 __hash__ = None:", OnlyEq.__hash__)
    try:
        {OnlyEq(1)}
    except TypeError as e:
        print("집합에 못 넣음:", e)

    item = MutableBadHash(1)
    s = {item}
    item.v = 2                               # 해시에 쓰인 필드를 바꿈
    print("바꾼 뒤 in 검사:", item in s, "| 그래도 들어 있음:", len(s))
    assert item not in s


class Deck:
    def __init__(self):
        self.cards = [f"{r}{s}" for s in "SH" for r in "A23"]

    def __len__(self):
        return len(self.cards)

    def __getitem__(self, i):                # 인덱스·슬라이스·순회·in까지 한 번에
        return self.cards[i]

    def __contains__(self, card):
        return card in set(self.cards)


def container_protocol():
    d = Deck()
    print("len:", len(d), "| d[0]:", d[0], "| 슬라이스:", d[1:3], "| 역순:", list(reversed(d))[:2])
    print("in:", "AS" in d, "| 순회:", [c for c in d][:3])
    import random
    random.seed(0)
    print("random.choice도 동작:", random.choice(d))


class Multiplier:
    def __init__(self, k):
        self.k = k

    def __call__(self, x):
        return x * self.k


class Spy:
    def __getattr__(self, name):            # 없는 속성 조회 때만 호출
        return f"<{name} 없음>"


def call_and_attr():
    triple = Multiplier(3)
    print("__call__:", triple(5), callable(triple), list(map(triple, [1, 2])))
    print("__getattr__:", Spy().anything)


def reflected_and_inplace():
    class Money:
        def __init__(self, v):
            self.v = v

        def __add__(self, other):
            return Money(self.v + (other.v if isinstance(other, Money) else other))

        def __radd__(self, other):           # sum()은 0 + Money로 시작한다
            return self.__add__(other)

        def __repr__(self):
            return f"Money({self.v})"
    print("sum과 __radd__:", sum([Money(1), Money(2), Money(3)]))


if __name__ == "__main__":
    basics()
    eq_hash_contract()
    container_protocol()
    call_and_attr()
    reflected_and_inplace()
    print("모든 검증 통과")
