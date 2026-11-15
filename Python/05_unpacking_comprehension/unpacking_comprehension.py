"""05. 언패킹·컴프리헨션·왈러스: 확장 언패킹, 컴프리헨션 스코프, 제너레이터 식, :="""
import re
import sys


def unpacking():
    a, b = 1, 2
    a, b = b, a                       # 오른쪽 튜플을 먼저 만든 뒤 왼쪽에 대입
    print("swap:", a, b)
    assert (a, b) == (2, 1)

    first, *middle, last = [1, 2, 3, 4, 5]
    print("확장 언패킹:", first, middle, last)
    assert middle == [2, 3, 4]        # 별표 쪽은 항상 리스트

    head, *tail = "abc"
    print("문자열도 이터러블:", head, tail)

    (x, y), z = (1, 2), 3             # 중첩 구조도 모양만 맞으면 된다
    for name, (lo, hi) in [("a", (0, 9)), ("b", (10, 19))]:
        pass
    print("중첩 언패킹:", x, y, z, name, lo, hi)
    assert (x, y, z, lo) == (1, 2, 3, 10)

    try:
        p, q = [1, 2, 3]
    except ValueError as e:
        print("개수 불일치:", e)

    merged = [*range(3), *"ab"]
    print("리터럴 안 언패킹:", merged, {*"aab"} == {"a", "b"})


def comprehensions():
    squares = [n * n for n in range(6) if n % 2 == 0]
    pairs = [(i, j) for i in range(3) for j in range(i)]    # 바깥 for가 먼저
    inverse = {v: k for k, v in {"a": 1, "b": 2}.items()}
    flags = ["even" if n % 2 == 0 else "odd" for n in range(4)]  # 조건식은 앞쪽
    print("squares:", squares)
    print("pairs:", pairs)
    print("inverse:", inverse, "| flags:", flags)
    assert pairs == [(1, 0), (2, 0), (2, 1)]

    n = "outer"
    _ = [n for n in range(3)]
    print("컴프리헨션 변수는 새지 않는다:", n)
    assert n == "outer"


def generator_expression():
    data = range(1_000_000)
    lst = [v * 2 for v in data]
    gen = (v * 2 for v in data)
    print("리스트 크기가 더 큼:", sys.getsizeof(lst) > 100 * sys.getsizeof(gen))
    print("sum(제너레이터 식):", sum(v * 2 for v in range(5)))   # 괄호 하나로 충분
    assert sum(v * 2 for v in range(5)) == 20

    gen2 = (v for v in range(3))
    print("한 번만 소비:", list(gen2), list(gen2))


def walrus():
    lines = ["id=1", "noise", "id=22"]
    ids = [int(m.group(1)) for line in lines if (m := re.match(r"id=(\d+)", line))]
    print("왈러스로 매칭 결과 재사용:", ids)
    assert ids == [1, 22]

    chunks, buf = [], iter("abcdefg")
    while (chunk := "".join(c for _, c in zip(range(3), buf))):
        chunks.append(chunk)
    print("while 조건에서 대입:", chunks)
    assert chunks == ["abc", "def", "g"]

    values = [3, 8, 1]
    if (n := len(values)) > 2:
        print(f"길이 {n}개라 처리")


if __name__ == "__main__":
    unpacking()
    comprehensions()
    generator_expression()
    walrus()
    print("모든 검증 통과")
