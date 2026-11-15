"""23. operator 모듈: itemgetter, attrgetter, methodcaller, 연산자 함수, 성능"""
import operator
import timeit
from dataclasses import dataclass
from functools import reduce

rows = [("kim", 30, "seoul"), ("lee", 25, "busan"), ("choi", 30, "incheon")]


@dataclass
class User:
    name: str
    age: int
    address: "Address"


@dataclass
class Address:
    city: str


def itemgetter_demo():
    by_age = sorted(rows, key=operator.itemgetter(1))
    by_age_name = sorted(rows, key=operator.itemgetter(1, 0))
    print("itemgetter(1):", [r[0] for r in by_age])
    print("itemgetter(1, 0):", [r[0] for r in by_age_name])
    get_name_city = operator.itemgetter(0, 2)
    print("여러 항목 → 튜플:", get_name_city(rows[0]))

    records = [{"id": 3, "score": 70}, {"id": 1, "score": 95}]
    print("dict 키:", max(records, key=operator.itemgetter("score")))
    print("슬라이스:", operator.itemgetter(slice(1, 3))("abcdef"))


def attrgetter_demo():
    users = [User("kim", 30, Address("seoul")), User("lee", 25, Address("busan"))]
    print("attrgetter('age'):", [u.name for u in sorted(users, key=operator.attrgetter("age"))])
    print("점 경로:", list(map(operator.attrgetter("address.city"), users)))
    print("여러 속성:", operator.attrgetter("name", "age")(users[0]))


def methodcaller_demo():
    words = ["  Apple ", "banana  ", " Cherry"]
    print("methodcaller('strip'):", list(map(operator.methodcaller("strip"), words)))
    split_comma = operator.methodcaller("split", ",", 1)
    print("인자 포함:", split_comma("a,b,c"))


def operator_functions():
    print("add, mul:", operator.add(2, 3), operator.mul(2, 3))
    print("reduce(mul):", reduce(operator.mul, range(1, 6)))
    print("sorted(key=neg):", sorted([3, 1, 2], key=operator.neg))
    print("contains:", operator.contains([1, 2], 2), "| truth:", operator.truth(""))
    ops = {"+": operator.add, "-": operator.sub, "*": operator.mul, "/": operator.truediv}

    def calc(expr):
        a, op, b = expr.split()
        return ops[op](float(a), float(b))
    print("연산자 디스패치:", calc("6 * 7"), calc("1 / 4"))
    print("in-place: iadd(list):", operator.iadd([1], [2]))


def performance():
    data = [(i, -i) for i in range(10_000)]
    t_lambda = timeit.timeit(lambda: sorted(data, key=lambda r: r[1]), number=50)
    t_getter = timeit.timeit(lambda: sorted(data, key=operator.itemgetter(1)), number=50)
    print(f"정렬 50회 - lambda: {t_lambda * 1000:.0f}ms, itemgetter: {t_getter * 1000:.0f}ms")


if __name__ == "__main__":
    itemgetter_demo()
    attrgetter_demo()
    methodcaller_demo()
    operator_functions()
    performance()
    assert operator.itemgetter(1, 0)(rows[0]) == (30, "kim")
    assert operator.attrgetter("address.city")(User("a", 1, Address("x"))) == "x"
    print("모든 검증 통과")
