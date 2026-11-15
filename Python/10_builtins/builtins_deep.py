"""10. 내장 함수 심화: sorted key·안정 정렬, min/max key·default, zip strict, enumerate, any/all, map/filter"""

students = [
    {"name": "kim", "grade": 2, "score": 90},
    {"name": "lee", "grade": 1, "score": 85},
    {"name": "park", "grade": 2, "score": 95},
    {"name": "choi", "grade": 1, "score": 85},
]


def sorting():
    by_score = sorted(students, key=lambda s: s["score"], reverse=True)
    print("점수 내림차순:", [s["name"] for s in by_score])

    multi = sorted(students, key=lambda s: (s["grade"], -s["score"]))
    print("학년 오름, 점수 내림:", [s["name"] for s in multi])
    assert [s["name"] for s in multi] == ["lee", "choi", "park", "kim"]

    # 안정 정렬: 키가 같으면 원래 순서 유지 → 여러 번 정렬해 다중 키 정렬
    step = sorted(students, key=lambda s: s["name"])         # 2차 키 먼저
    step = sorted(step, key=lambda s: s["score"], reverse=True)  # 1차 키 나중
    print("두 번 정렬(점수 내림, 동점은 이름순):", [s["name"] for s in step])
    assert [s["name"] for s in step] == ["park", "kim", "choi", "lee"]

    words = ["banana", "apple", "Cherry"]
    print("기본 정렬:", sorted(words), "| 대소문자 무시:", sorted(words, key=str.lower))
    print("길이순:", sorted(words, key=len))


def min_max():
    best = max(students, key=lambda s: s["score"])
    print("최고점:", best["name"])
    print("빈 시퀀스 default:", max([], default=None), min([], default=0))
    try:
        max([])
    except ValueError as e:
        print("default 없으면:", e)
    print("여러 인자:", max(3, 7, 5), min("bca"))


def zip_enumerate():
    names, scores = ["a", "b", "c"], [1, 2]
    print("zip 짧은 쪽 기준:", list(zip(names, scores)))
    try:
        list(zip(names, scores, strict=True))     # 3.10+
    except ValueError as e:
        print("strict=True:", e)

    matrix = [[1, 2, 3], [4, 5, 6]]
    print("전치(zip(*m)):", list(zip(*matrix)))
    keys, values = zip(*{"x": 1, "y": 2}.items())
    print("unzip:", keys, values)

    for i, name in enumerate(names, start=1):
        print(f"  {i}. {name}")
    print("dict(zip()):", dict(zip(names, range(3))))


def any_all():
    nums = [2, 4, 6]
    print("all 짝수:", all(n % 2 == 0 for n in nums), "| any 5 초과:", any(n > 5 for n in nums))
    print("빈 시퀀스:", all([]), any([]))
    assert all([]) is True and any([]) is False

    checked = []

    def is_big(n):
        checked.append(n)
        return n > 3
    any(is_big(n) for n in [1, 5, 2, 8])
    print("any는 단락 평가:", checked)
    assert checked == [1, 5]


def map_filter():
    nums = ["1", "2", "x", "4"]
    print("map(int, ...):", list(map(int, filter(str.isdigit, nums))))
    print("컴프리헨션:", [int(n) for n in nums if n.isdigit()])
    print("map 여러 이터러블:", list(map(pow, [2, 3], [3, 2])))
    print("filter(None, ...):", list(filter(None, [0, 1, "", "a", None, []])))


def misc():
    print("divmod:", divmod(17, 5), "| round 은행원 반올림:", round(0.5), round(1.5), round(2.5))
    assert (round(0.5), round(2.5)) == (0, 2)
    print("sum start:", sum([[1], [2]], start=[]), "| sum([0.1]*10):", sum([0.1] * 10))
    total = 0.0
    for v in [0.1] * 10:
        total += v
    print("반복문 += 합계:", total)
    assert sum([0.1] * 10) == 1.0 and total != 1.0   # 3.12+: sum은 보정 합산
    import math
    print("math.fsum:", math.fsum([0.1] * 10))
    print("reversed:", list(reversed(range(3))), "| isinstance 튜플:", isinstance(3, (int, float)))
    print("getattr 기본값:", getattr(object(), "missing", "없음"))


if __name__ == "__main__":
    sorting()
    min_max()
    zip_enumerate()
    any_all()
    map_filter()
    misc()
    print("모든 검증 통과")
