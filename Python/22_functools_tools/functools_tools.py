"""22. functools ② 함수 도구: partial, partialmethod, reduce, wraps, singledispatch, total_ordering, cmp_to_key"""
import functools
import json
import operator
from datetime import date
from decimal import Decimal


def partial_demo():
    def power(base, exp):
        return base ** exp

    square = functools.partial(power, exp=2)
    cube = functools.partial(power, exp=3)
    print("partial:", square(5), cube(2), "| 고정 인자:", square.keywords)

    to_int_base2 = functools.partial(int, base=2)
    print("int(base=2):", to_int_base2("1011"))

    dumps_kr = functools.partial(json.dumps, ensure_ascii=False, indent=None, sort_keys=True)
    print("설정 고정 json.dumps:", dumps_kr({"이름": "kim", "age": 3}))

    callbacks = [functools.partial(print, "  작업", i) for i in range(2)]
    for cb in callbacks:
        cb()


class Light:
    def _set(self, on):
        self.on = on

    turn_on = functools.partialmethod(_set, True)
    turn_off = functools.partialmethod(_set, False)


def reduce_demo():
    nums = [3, 1, 4, 1, 5]
    print("reduce(add):", functools.reduce(operator.add, nums), "| sum:", sum(nums))
    print("reduce(mul, 초기값):", functools.reduce(operator.mul, nums, 1))
    nested = {"a": {"b": {"c": 42}}}
    print("중첩 조회:", functools.reduce(operator.getitem, ["a", "b", "c"], nested))
    print("빈 입력 + 초기값:", functools.reduce(operator.add, [], 0))
    l = Light()
    l.turn_on()
    print("partialmethod:", l.on)


def wraps_demo():
    def deco(f):
        @functools.wraps(f)
        def wrapper(*a, **k):
            return f(*a, **k)
        return wrapper

    @deco
    def area(r):
        """원의 넓이"""
        return 3.14 * r * r
    print("wraps 복사 속성:", area.__name__, area.__doc__, area.__wrapped__.__name__)
    print("WRAPPER_ASSIGNMENTS:", functools.WRAPPER_ASSIGNMENTS)


@functools.singledispatch
def to_json(value):
    raise TypeError(f"지원하지 않는 타입: {type(value).__name__}")


@to_json.register
def _(value: date):
    return value.isoformat()


@to_json.register
def _(value: Decimal):
    return str(value)


@to_json.register(set)
@to_json.register(frozenset)
def _(value):
    return sorted(value)


@to_json.register
def _(value: int | float):           # 3.11+: 유니온 타입으로 등록
    return value


def singledispatch_demo():
    print("singledispatch:", to_json(date(2026, 11, 15)), to_json(Decimal("1.10")), to_json({3, 1}), to_json(7))
    print("bool은 int 하위 클래스라 int 구현 사용:", to_json(True))
    try:
        to_json([1])
    except TypeError as e:
        print("등록 안 된 타입:", e)
    print("dispatch(bool):", to_json.dispatch(bool).__name__)
    print("json.dumps(default=):", json.dumps({"d": date(2026, 1, 1), "n": Decimal("2.5")}, default=to_json))


class SingleMethod:
    @functools.singledispatchmethod
    def handle(self, arg):
        return f"기본: {arg!r}"

    @handle.register
    def _(self, arg: int):
        return f"int: {arg + 1}"


@functools.total_ordering
class Money:
    def __init__(self, amount):
        self.amount = amount

    def __eq__(self, other):
        return isinstance(other, Money) and self.amount == other.amount

    def __lt__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount < other.amount

    def __repr__(self):
        return f"Money({self.amount})"


def ordering_demo():
    a, b = Money(100), Money(200)
    print("total_ordering:", a < b, a <= b, a > b, a >= b, "| 정렬:", sorted([b, a]))
    assert (a >= b) is False

    def compare(x, y):                      # 옛 방식 비교 함수: 음수/0/양수
        return (len(x) > len(y)) - (len(x) < len(y)) or (x > y) - (x < y)
    words = ["bb", "a", "ccc", "ab"]
    print("cmp_to_key:", sorted(words, key=functools.cmp_to_key(compare)))
    print("SingleMethod:", SingleMethod().handle(41), SingleMethod().handle("x"))


if __name__ == "__main__":
    partial_demo()
    reduce_demo()
    wraps_demo()
    singledispatch_demo()
    ordering_demo()
    print("모든 검증 통과")
