"""25. enum 심화: Enum, auto, 값·이름 조회, unique, IntEnum·StrEnum, Flag, 메서드와 match"""
import enum
from enum import Enum, Flag, IntEnum, StrEnum, auto, unique


class Status(Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    CANCELED = "canceled"

    @property
    def is_final(self):
        return self in (Status.SHIPPED, Status.CANCELED)

    @classmethod
    def from_label(cls, label):
        return cls(label.lower())


def basics():
    s = Status.PAID
    print("멤버:", s, "| name:", s.name, "| value:", s.value, "| repr:", repr(s))
    print("값으로 조회:", Status("shipped"), "| 이름으로 조회:", Status["CANCELED"])
    print("순회:", [m.name for m in Status], "| 개수:", len(Status))
    print("is 비교:", Status("paid") is Status.PAID)
    print("문자열과 같지 않다:", Status.PAID == "paid")
    print("메서드·속성:", Status.from_label("PENDING"), Status.SHIPPED.is_final, Status.PAID.is_final)
    try:
        Status("refund")
    except ValueError as e:
        print("없는 값:", e)
    try:
        Status.PAID = "x"
    except AttributeError as e:
        print("재할당 불가:", type(e).__name__)


class Color(Enum):
    RED = auto()
    GREEN = auto()
    CRIMSON = 1            # RED와 값이 같으면 별칭(alias)


def aliases_and_unique():
    print("auto 값:", [(m.name, m.value) for m in Color], "| 별칭:", Color.CRIMSON is Color.RED)
    print("__members__에는 별칭 포함:", list(Color.__members__))
    try:
        @unique
        class Dup(Enum):
            A = 1
            B = 1
    except ValueError as e:
        print("@unique:", e)


class Priority(IntEnum):
    LOW = 1
    HIGH = 3


class Env(StrEnum):           # 3.11+
    DEV = auto()              # StrEnum에서 auto()는 소문자 이름
    PROD = auto()


def int_str_enums():
    print("IntEnum은 int:", Priority.HIGH > Priority.LOW, Priority.HIGH + 1, Priority.HIGH == 3)
    print("정렬:", sorted([Priority.HIGH, Priority.LOW]))
    print("StrEnum은 str:", Env.DEV == "dev", f"{Env.PROD}", Env("prod"))
    print("StrEnum auto 값:", [e.value for e in Env])


class Perm(Flag):
    READ = auto()
    WRITE = auto()
    EXEC = auto()
    RW = READ | WRITE


def flags():
    p = Perm.READ | Perm.EXEC
    print("Flag 조합:", p, "| 값:", p.value)
    print("포함 검사:", Perm.READ in p, Perm.WRITE in p)
    print("멤버 순회(3.11+):", [m.name for m in p])
    print("조합 별칭:", Perm.RW, "| 비어 있음:", bool(Perm(0)))
    assert Perm.WRITE not in p


def with_match(status):
    match status:
        case Status.PENDING | Status.PAID:
            return "처리 중"
        case Status.SHIPPED:
            return "배송됨"
        case _:
            return "종료"


def functional_api():
    Weekday = Enum("Weekday", "MON TUE WED")
    print("함수형 API:", list(Weekday), Weekday.TUE.value)
    print("enum.verify(CONTINUOUS) 사용 가능:", hasattr(enum, "verify"))


if __name__ == "__main__":
    basics()
    aliases_and_unique()
    int_str_enums()
    flags()
    print("match:", [with_match(s) for s in Status])
    functional_api()
    print("모든 검증 통과")
