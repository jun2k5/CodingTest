"""04. 함수 인자 심화: *args·**kwargs, 위치 전용 /, 키워드 전용 *, 가변 기본값 함정"""
import inspect


def collect(*args, **kwargs):
    return args, kwargs


def signature_kinds(a, b=2, /, c=3, *args, d, e=5, **kwargs):
    return a, b, c, args, d, e, kwargs


def append_bad(item, target=[]):
    target.append(item)
    return target


def append_good(item, target=None):
    if target is None:
        target = []
    target.append(item)
    return target


_MISSING = object()


def get_option(options, key, default=_MISSING):
    """None도 정상 값으로 받아야 할 때 쓰는 센티널 패턴"""
    if key in options:
        return options[key]
    if default is _MISSING:
        raise KeyError(key)
    return default


def wrapper(*args, **kwargs):
    """받은 인자를 그대로 다른 함수로 넘기는 전형적인 패턴"""
    return signature_kinds(*args, **kwargs)


def demo():
    print("collect(1, 2, x=3):", collect(1, 2, x=3))
    assert collect(1, 2, x=3) == ((1, 2), {"x": 3})

    print("signature_kinds(1, d=4):", signature_kinds(1, d=4))
    assert signature_kinds(1, d=4) == (1, 2, 3, (), 4, 5, {})
    print("signature_kinds(1, 2, 3, 9, 9, d=4, z=0):", signature_kinds(1, 2, 3, 9, 9, d=4, z=0))

    for bad_call, label in [
        (lambda: signature_kinds(a=1, d=4), "a를 키워드로"),
        (lambda: signature_kinds(1, 2, 3, 4), "d를 위치로"),
    ]:
        try:
            bad_call()
        except TypeError as e:
            print(f"{label}: TypeError")
            assert "positional" in str(e) or "keyword" in str(e)

    kinds = {name: p.kind.name for name, p in inspect.signature(signature_kinds).parameters.items()}
    print("매개변수 종류:", kinds)
    assert kinds["a"] == "POSITIONAL_ONLY" and kinds["d"] == "KEYWORD_ONLY"

    print("append_bad:", append_bad(1), append_bad(2))
    print("기본값 객체:", append_bad.__defaults__)
    assert append_bad.__defaults__ == ([1, 2],)
    print("append_good:", append_good(1), append_good(2))
    assert append_good(3) == [3]

    print("센티널:", get_option({"x": None}, "x"), get_option({}, "y", 0))
    try:
        get_option({}, "z")
    except KeyError:
        print("기본값 없으면 KeyError")

    args, kwargs = (1,), {"d": 4, "e": 6}
    print("언패킹 전달:", wrapper(*args, **kwargs))
    assert wrapper(*args, **kwargs) == (1, 2, 3, (), 4, 6, {})

    merged = {**{"a": 1, "b": 2}, **{"b": 3}}
    print("딕셔너리 병합:", merged, "| | 연산자:", {"a": 1} | {"a": 9})
    assert merged == {"a": 1, "b": 3}


if __name__ == "__main__":
    demo()
    print("모든 검증 통과")
