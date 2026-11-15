"""16. dataclasses 심화: 생성되는 메서드, field, __post_init__, frozen, order, slots, kw_only, replace"""
import dataclasses
import sys
from dataclasses import InitVar, KW_ONLY, dataclass, field


@dataclass
class Item:
    name: str
    price: int
    tags: list[str] = field(default_factory=list)       # 가변 기본값은 default_factory
    secret: str = field(default="", repr=False, compare=False)


def generated_methods():
    a = Item("pen", 1000)
    b = Item("pen", 1000, secret="x")
    a.tags.append("office")
    print("repr:", a)
    print("eq(secret 비교 제외):", a == Item("pen", 1000, ["office"]), "| b == a:", b == Item("pen", 1000))
    print("필드:", [f.name for f in dataclasses.fields(Item)])
    print("__hash__ 기본값:", Item.__hash__)               # eq=True, frozen=False → None
    assert Item.__hash__ is None

    try:
        @dataclass
        class Bad:
            items: list = []
    except ValueError as e:
        print("가변 기본값 금지:", e)


@dataclass
class Order:
    unit_price: int
    quantity: int
    discount_rate: InitVar[float] = 0.0                 # __init__에만 받고 필드로 저장 안 함
    total: int = field(init=False)

    def __post_init__(self, discount_rate):
        if self.quantity <= 0:
            raise ValueError("수량은 1 이상")
        self.total = round(self.unit_price * self.quantity * (1 - discount_rate))


def post_init():
    o = Order(1000, 3, discount_rate=0.1)
    print("__post_init__ 계산:", o)
    print("인스턴스에 저장 안 됨:", "discount_rate" in vars(o),
          "| 기본값은 클래스 속성으로 남음:", Order.discount_rate)
    assert o.total == 2700 and "discount_rate" not in vars(o)
    try:
        Order(1000, 0)
    except ValueError as e:
        print("검증 실패:", e)


@dataclass(frozen=True, order=True)
class Version:
    major: int
    minor: int = 0
    patch: int = 0


def frozen_and_order():
    v = Version(1, 2)
    try:
        v.major = 2
    except dataclasses.FrozenInstanceError as e:
        print("frozen:", type(e).__name__)
    print("정렬:", sorted([Version(1, 10), Version(1, 2, 5), Version(0, 9)]))
    print("해시 가능 → 집합:", {Version(1), Version(1, 0, 0)})
    print("replace:", dataclasses.replace(v, minor=3))
    assert Version(1, 10) > Version(1, 2, 5)


@dataclass(slots=True)
class SlotPoint:
    x: int
    y: int


@dataclass
class DictPoint:
    x: int
    y: int


def slots():
    sp, dp = SlotPoint(1, 2), DictPoint(1, 2)
    print("__dict__ 있음:", hasattr(sp, "__dict__"), hasattr(dp, "__dict__"))
    size_slot = sys.getsizeof(sp)
    size_dict = sys.getsizeof(dp) + sys.getsizeof(dp.__dict__)
    print(f"크기: slots {size_slot}B, 일반 {size_dict}B")
    try:
        sp.z = 3
    except AttributeError:
        print("slots: 새 속성 추가 불가")
    assert size_slot < size_dict


@dataclass
class Base:
    id: int
    created: str = "today"


@dataclass(kw_only=True)
class Child(Base):
    name: str                       # 기본값 없는 필드가 기본값 있는 필드 뒤에 와도 됨


@dataclass
class Mixed:
    a: int
    _: KW_ONLY
    b: int = 0
    c: int


def kw_only():
    print("kw_only 상속:", Child(1, name="kim"))
    print("KW_ONLY 표시:", Mixed(1, c=3))
    try:
        Mixed(1, 2, 3)
    except TypeError:
        print("키워드 전용은 위치로 못 넘김")


def to_dict_and_tuple():
    o = Item("cup", 500, ["kitchen"])
    print("asdict:", dataclasses.asdict(o), "| astuple:", dataclasses.astuple(o))


if __name__ == "__main__":
    generated_methods()
    post_init()
    frozen_and_order()
    slots()
    kw_only()
    to_dict_and_tuple()
    print("모든 검증 통과")
