"""03. 스코프와 클로저: LEGB, global·nonlocal, 클로저 셀, 늦은 바인딩"""
import functools

x = "global"


def legb():
    x = "enclosing"

    def inner():
        # L(지역)에 x가 없으니 E(감싸는 함수) → G(전역) → B(내장) 순으로 찾는다
        return x, len  # len은 B(builtins)에서 찾는다

    found, builtin = inner()
    print("inner가 찾은 x:", found, "| len:", builtin.__module__)
    assert found == "enclosing" and builtin is len


def unbound_local():
    count = 0

    def bad():
        try:
            count += 1  # 대입이 있으니 count는 '지역 변수'로 컴파일된다
        except UnboundLocalError as e:
            return type(e).__name__
    result = bad()
    print("대입 전 읽기:", result)
    assert result == "UnboundLocalError"


def global_and_nonlocal():
    global x
    x = "changed by global"

    def make_counter():
        count = 0

        def increment():
            nonlocal count  # 감싸는 함수의 count를 다시 묶는다
            count += 1
            return count
        return increment

    c1, c2 = make_counter(), make_counter()
    print("c1:", c1(), c1(), c1(), "| c2:", c2())
    assert (c1(), c2()) == (4, 2)
    print("전역 x:", x)
    assert x == "changed by global"


def closure_cells():
    def make_multiplier(n):
        def multiply(v):
            return v * n
        return multiply

    times3 = make_multiplier(3)
    print("자유 변수:", times3.__code__.co_freevars,
          "| 셀 내용:", times3.__closure__[0].cell_contents)
    assert times3(5) == 15 and times3.__closure__[0].cell_contents == 3


def late_binding():
    funcs = [lambda: i for i in range(3)]
    late = [f() for f in funcs]
    print("늦은 바인딩:", late)
    assert late == [2, 2, 2]  # 호출 시점의 i(마지막 값)를 읽는다

    fixed_default = [lambda i=i: i for i in range(3)]
    fixed_partial = [functools.partial(lambda i: i, i) for i in range(3)]
    print("기본값으로 고정:", [f() for f in fixed_default],
          "| partial:", [f() for f in fixed_partial])
    assert [f() for f in fixed_default] == [0, 1, 2] == [f() for f in fixed_partial]


def class_scope():
    class Config:
        factor = 10
        # 클래스 몸체는 감싸는 스코프(E)가 되지 않는다:
        # 컴프리헨션 안에서는 factor를 볼 수 없다(첫 이터러블만 클래스 스코프에서 평가)
        try:
            values = [factor * n for n in range(3)]
        except NameError as e:
            values = f"NameError: {e}"
    print("클래스 몸체 컴프리헨션:", Config.values)
    assert str(Config.values).startswith("NameError")


if __name__ == "__main__":
    legb()
    unbound_local()
    global_and_nonlocal()
    closure_cells()
    late_binding()
    class_scope()
    print("모든 검증 통과")
