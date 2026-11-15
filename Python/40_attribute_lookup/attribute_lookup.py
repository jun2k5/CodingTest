"""40. 속성 조회와 __slots__: 조회 순서, __getattr__ vs __getattribute__, __setattr__, __slots__ 메모리와 제약"""
import sys
import tracemalloc


class Base:
    shared = "클래스 속성"

    def method(self):
        return "메서드"


def lookup_order():
    b = Base()
    print("인스턴스 → 클래스:", b.shared, "| __dict__:", vars(b))
    b.shared = "인스턴스 속성"                  # 인스턴스에 같은 이름 → 가린다
    print("가린 뒤:", b.shared, "| 클래스는 그대로:", Base.shared)
    del b.shared
    print("del 후 다시 클래스 속성:", b.shared)
    b.method = lambda: "인스턴스에 붙인 함수"     # 함수(비데이터 디스크립터)는 인스턴스 dict가 이긴다
    print("메서드 가리기:", b.method())


class Config:
    """__getattr__: 일반 조회가 실패했을 때만 호출"""

    def __init__(self, data):
        self._data = data

    def __getattr__(self, name):
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError(f"설정 없음: {name}") from None


class Audited:
    """__getattribute__: 모든 속성 접근에 호출 — super()로 위임하지 않으면 무한 재귀"""

    def __init__(self):
        self.value = 1
        self.log = []

    def __getattribute__(self, name):
        if name != "log":
            object.__getattribute__(self, "log").append(name)
        return super().__getattribute__(name)


class Frozenish:
    """__setattr__: 모든 대입을 가로챈다"""

    def __init__(self, x):
        object.__setattr__(self, "x", x)

    def __setattr__(self, name, value):
        raise AttributeError(f"{name}을(를) 바꿀 수 없음")


def hooks():
    c = Config({"host": "localhost", "port": 8000})
    print("__getattr__:", c.host, c.port, "| 일반 속성은 그대로:", type(c._data).__name__)
    print("hasattr(없는 설정):", hasattr(c, "debug"))
    a = Audited()
    _ = a.value
    _ = a.value
    print("__getattribute__ 기록:", a.log)
    f = Frozenish(1)
    try:
        f.x = 2
    except AttributeError as e:
        print("__setattr__:", e)


class PointDict:
    def __init__(self, x, y):
        self.x, self.y = x, y


class PointSlots:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x, self.y = x, y


def measure(cls, n=100_000):
    tracemalloc.start()
    objs = [cls(i, i) for i in range(n)]
    current, _ = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    del objs
    return current / n


def slots():
    p, s = PointDict(1, 2), PointSlots(1, 2)
    print("__dict__ 유무:", hasattr(p, "__dict__"), hasattr(s, "__dict__"))
    print("slot은 디스크립터:", type(PointSlots.x).__name__)
    per_dict, per_slot = measure(PointDict), measure(PointSlots)
    print(f"객체당 메모리(10만 개 평균): dict {per_dict:.0f}B, slots {per_slot:.0f}B")
    assert per_slot < per_dict
    try:
        s.z = 3
    except AttributeError as e:
        print("새 속성 추가 불가:", e)

    class Child(PointSlots):                     # 하위 클래스가 __slots__를 안 쓰면 __dict__가 다시 생긴다
        pass
    print("__slots__ 없는 자식에 __dict__:", hasattr(Child(1, 2), "__dict__"))

    class ChildSlots(PointSlots):
        __slots__ = ("z",)                       # 부모 slot은 다시 쓰지 않는다
    cs = ChildSlots(1, 2)
    cs.z = 3
    print("자식도 __slots__:", hasattr(cs, "__dict__"), cs.x, cs.z)


if __name__ == "__main__":
    lookup_order()
    hooks()
    slots()
    print("sys.getsizeof 비교(얕은 크기):", sys.getsizeof(PointSlots(1, 2)) < sys.getsizeof(PointDict(1, 2)) + sys.getsizeof({}))
    print("모든 검증 통과")
