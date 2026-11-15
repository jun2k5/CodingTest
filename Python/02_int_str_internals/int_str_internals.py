"""02. 정수와 문자열 내부: 작은 정수 캐시, 인터닝, str 불변성과 join, f-string"""
import sys
import timeit


def small_int_cache():
    # 상수 접기(constant folding)를 피하려고 런타임에 int()로 만든다
    a, b = int("256"), int("256")
    c, d = int("257"), int("257")
    print("256 is 256:", a is b, "| 257 is 257:", c is d)
    assert a is b            # CPython은 -5~256을 미리 만들어 재사용한다
    assert c is not d        # 그 밖의 정수는 만들 때마다 새 객체
    assert c == d


def big_int():
    n = 2 ** 200
    print("2**200 자릿수:", len(str(n)))
    assert n.bit_length() == 201
    print("int 크기(바이트):", sys.getsizeof(0) <= sys.getsizeof(n))
    # 3.11+: 10진 문자열 변환 길이 제한 (보안상 기본 4300자리)
    print("int 문자열 제한:", sys.get_int_max_str_digits())
    assert sys.get_int_max_str_digits() == 4300


def interning():
    s1 = "".join(["hello", "_", "world"])   # 런타임에 만든 문자열
    s2 = "hello_world"
    print("런타임 문자열 is 리터럴:", s1 is s2)
    assert s1 == s2 and s1 is not s2
    i1, i2 = sys.intern(s1), sys.intern(s2)
    print("sys.intern 후:", i1 is i2)
    assert i1 is i2


def immutability_and_join():
    words = [str(i) for i in range(1000)]

    def concat():
        s = ""
        for w in words:
            s += w
        return s

    def joined():
        return "".join(words)

    assert concat() == joined()
    t_concat = min(timeit.repeat(concat, number=200, repeat=5))
    t_join = min(timeit.repeat(joined, number=200, repeat=5))
    print(f"+= 연결: {t_concat * 1000:.1f}ms, join: {t_join * 1000:.1f}ms (200회, 실행마다 다름)")


def code_points_and_bytes():
    s = "파이썬"
    print("len:", len(s), "| utf-8 바이트:", len(s.encode("utf-8")))
    assert len(s) == 3 and len(s.encode("utf-8")) == 9
    print("ord('파'):", ord("파"), "| chr(54028):", chr(54028))
    assert chr(ord("파")) == "파"


def fstring_features():
    price, name = 1234567.891, "kim"
    print(f"{price:,.2f}")            # 천 단위 구분, 소수 둘째 자리
    print(f"[{name:>6}] [{name:<6}] [{name:^7}]")
    print(f"{name!r} {name=}")        # !r: repr, = : 식과 값 함께(3.8+)
    print(f"{255:#x} {255:08b} {0.25:.0%}")
    width = 8
    print(f"[{'nested':>{width}}]")   # 중첩 서식 지정
    items = {"a": 1}
    print(f"{items["a"]}")            # 3.12+: 같은 따옴표 재사용 가능 (PEP 701)
    assert f"{price:,.2f}" == "1,234,567.89"
    assert f"{name=}" == "name='kim'"


if __name__ == "__main__":
    small_int_cache()
    big_int()
    interning()
    immutability_and_join()
    code_points_and_bytes()
    fstring_features()
    print("모든 검증 통과")
