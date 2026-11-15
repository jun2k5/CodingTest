"""15. 레코드 타입 비교: tuple, namedtuple, typing.NamedTuple, dataclass, TypedDict, 일반 클래스"""
import sys
from collections import namedtuple
from dataclasses import asdict, dataclass
from typing import NamedTuple, TypedDict

PointNT = namedtuple("PointNT", ["x", "y"])


class PointTN(NamedTuple):
    x: int
    y: int = 0

    def dist2(self):
        return self.x ** 2 + self.y ** 2


@dataclass
class PointDC:
    x: int
    y: int = 0


class PointTD(TypedDict):
    x: int
    y: int


class PointPlain:
    def __init__(self, x, y=0):
        self.x, self.y = x, y


def compare():
    t = (3, 4)
    nt = PointNT(3, 4)
    tn = PointTN(3, 4)
    dc = PointDC(3, 4)
    td: PointTD = {"x": 3, "y": 4}
    plain = PointPlain(3, 4)

    print("repr:", " | ".join(map(str, [nt, tn, dc, td])))
    print("일반 클래스 repr:", repr(plain).split(" at ")[0] + ">")
    print("이름 접근:", nt.x, tn.x, dc.x, td["x"], plain.x)
    print("튜플처럼 언패킹:", tuple(nt), tuple(tn))
    print("tuple과 같은가:", nt == t, tn == t, "| dataclass:", dc == PointDC(3, 4))
    assert nt == t and tn == t           # namedtuple은 tuple의 하위 클래스
    assert dc != t

    print("TypedDict 실체는 dict:", type(td).__name__)
    assert type(td) is dict


def mutability():
    nt = PointNT(1, 2)
    try:
        nt.x = 10
    except AttributeError as e:
        print("namedtuple 불변:", e)
    print("_replace:", nt._replace(x=10), "| _asdict:", nt._asdict())

    dc = PointDC(1, 2)
    dc.x = 10
    print("dataclass 가변:", dc, "| asdict:", asdict(dc))


def memory():
    sizes = {
        "tuple": sys.getsizeof((1, 2)),
        "namedtuple": sys.getsizeof(PointNT(1, 2)),
        "dataclass": sys.getsizeof(PointDC(1, 2)) + sys.getsizeof(PointDC(1, 2).__dict__),
        "dict": sys.getsizeof({"x": 1, "y": 2}),
    }
    print("인스턴스 크기(바이트, 대략):", sizes)
    assert sizes["namedtuple"] == sizes["tuple"]   # 이름은 클래스에 있고 인스턴스는 튜플 그대로


def typed_namedtuple():
    p = PointTN(3)
    print("기본값·메서드:", p, p.dist2(), "| 필드:", PointTN._fields)
    assert p.y == 0 and p.dist2() == 9


if __name__ == "__main__":
    compare()
    mutability()
    memory()
    typed_namedtuple()
    print("모든 검증 통과")
