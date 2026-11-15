"""26. typing 심화: Protocol vs abc, 제네릭(3.12 문법), type 별칭, Literal, overload, TypedDict, TypeIs, 3.14 지연 어노테이션"""
import abc
from typing import Literal, NotRequired, Protocol, Self, TypedDict, TypeIs, get_type_hints, overload, runtime_checkable


# --- 명목적(abc) vs 구조적(Protocol) 타이핑 ---
class Shape(abc.ABC):
    @abc.abstractmethod
    def area(self) -> float: ...


class Square(Shape):
    def __init__(self, side: float):
        self.side = side

    def area(self) -> float:
        return self.side ** 2


@runtime_checkable
class SupportsClose(Protocol):
    def close(self) -> None: ...


class Connection:                       # SupportsClose를 상속하지 않았다
    def close(self) -> None:
        print("  연결 닫음")


def close_all(items: list[SupportsClose]) -> None:
    for it in items:
        it.close()


def nominal_vs_structural():
    try:
        Shape()
    except TypeError as e:
        print("abc 추상 클래스:", str(e)[:60])
    print("Square는 Shape:", isinstance(Square(2), Shape), Square(2).area())
    print("Protocol 구조 검사:", isinstance(Connection(), SupportsClose), isinstance(3, SupportsClose))
    close_all([Connection()])


# --- 제네릭: 3.12+ 타입 매개변수 문법과 type 별칭 ---
def first[T](items: list[T]) -> T:
    return items[0]


class Stack[T]:
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> Self:
        self._items.append(item)
        return self

    def pop(self) -> T:
        return self._items.pop()


type Pair[K, V] = tuple[K, V]
type JSON = dict[str, JSON] | list[JSON] | str | int | float | bool | None


def generics():
    s = Stack[int]().push(1).push(2)
    print("제네릭 함수·클래스:", first(["a", "b"]), s.pop(), "| 타입 매개변수:", Stack.__type_params__)
    print("type 별칭:", Pair, "| 값:", Pair.__value__, "| 재귀 별칭 정의 가능:", JSON.__name__)


# --- Literal, overload ---
Mode = Literal["r", "w"]


def open_mode(mode: Mode) -> str:
    return f"mode={mode}"


@overload
def parse(value: str) -> int: ...
@overload
def parse(value: bytes) -> str: ...
def parse(value):
    return int(value) if isinstance(value, str) else value.decode()


def literal_overload():
    print("Literal(실행 시 검사 없음):", open_mode("r"), open_mode("x"))  # type: ignore[arg-type]
    print("overload 구현:", parse("42"), parse(b"hi"))


# --- TypedDict, TypeIs ---
class Movie(TypedDict):
    title: str
    year: NotRequired[int]


def is_str_list(values: list[object]) -> TypeIs[list[str]]:       # 3.13+
    return all(isinstance(v, str) for v in values)


def narrowing():
    m: Movie = {"title": "Dune"}
    print("TypedDict NotRequired:", m, "| 실체:", type(m).__name__)
    data: list[object] = ["a", "b"]
    if is_str_list(data):
        print("TypeIs 좁히기 후 문자열 메서드:", [v.upper() for v in data])


# --- 어노테이션은 실행 시 강제되지 않는다 + 3.14 지연 평가 ---
def greet(name: str) -> str:
    return "hi " + str(name)


def later_defined(x: NotYetDefined) -> None:     # 3.14+: 아직 없는 이름도 따옴표 없이(지연 평가, PEP 649)
    pass


class NotYetDefined:
    pass


def runtime_behavior():
    print("힌트와 다른 인자도 실행됨:", greet(123))
    print("get_type_hints:", get_type_hints(greet))
    print("앞쪽에서 뒤의 클래스 참조:", get_type_hints(later_defined)["x"].__name__)


if __name__ == "__main__":
    nominal_vs_structural()
    generics()
    literal_overload()
    narrowing()
    runtime_behavior()
    print("모든 검증 통과")
