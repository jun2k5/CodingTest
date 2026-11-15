"""37. 구조적 패턴 매칭(3.10+): 리터럴·캡처·와일드카드, 시퀀스·매핑·클래스 패턴, OR·as·가드, 값 패턴 함정"""
from dataclasses import dataclass


def command(text):
    match text.split():
        case ["quit" | "exit"]:
            return "종료"
        case ["go", direction]:
            return f"{direction}쪽으로 이동"
        case ["get", item, *rest] if rest:
            return f"{item} 외 {len(rest)}개 줍기"
        case ["get", item]:
            return f"{item} 줍기"
        case []:
            return "빈 입력"
        case _:
            return "알 수 없는 명령"


def handle_event(event):
    match event:
        case {"type": "click", "pos": [x, y]}:
            return f"클릭 ({x}, {y})"
        case {"type": "key", "key": str(key)} if len(key) == 1:
            return f"키 {key!r}"
        case {"type": "key", "key": key}:
            return f"특수 키 {key}"
        case {"type": "scroll", **rest}:
            return f"스크롤, 나머지 필드 {sorted(rest)}"
        case {"type": t}:
            return f"처리 안 하는 이벤트 {t}"
        case _:
            return "형식 오류"


@dataclass
class Point:
    x: int
    y: int


@dataclass
class Circle:
    center: Point
    r: float


@dataclass
class Rect:
    top_left: Point
    w: float
    h: float


def describe(shape):
    match shape:
        case Circle(center=Point(x=0, y=0), r=r):
            return f"원점 중심 원 r={r}"
        case Circle(Point(x, y), r) if r > 10:            # dataclass는 __match_args__로 위치 패턴 지원
            return f"큰 원 ({x},{y})"
        case Circle():
            return "작은 원"
        case Rect(w=w, h=h) if w == h:
            return f"정사각형 {w}"
        case Rect(top_left=Point() as p) | (Point() as p):   # as로 묶기, OR 양쪽이 같은 이름을 묶어야 함
            return f"점 기준 도형 {p}"
        case int(n) | float(n):
            return f"숫자 {n}"
        case _:
            return "모름"


RED = "red"


class Colors:
    RED = "red"


def value_pattern_trap(color):
    results = []
    match color:
        case Colors.RED:          # 점이 있는 이름 → 값 비교
            results.append("Colors.RED와 같음")
    match color:
        case other:               # 점이 없는 이름 → 캡처(무엇이든 맞는다)
            results.append(f"캡처 패턴이 {other!r}를 잡음")
    return results


def evaluate(expr):
    """작은 계산기: 중첩 튜플 구조를 재귀로 분해"""
    match expr:
        case int() | float():
            return expr
        case ("+", a, b):
            return evaluate(a) + evaluate(b)
        case ("*", a, b):
            return evaluate(a) * evaluate(b)
        case ("-", a):
            return -evaluate(a)
        case _:
            raise ValueError(f"잘못된 식: {expr!r}")


if __name__ == "__main__":
    for t in ["quit", "go north", "get key", "get key coin gem", "", "dance"]:
        print(f"{t!r:20} → {command(t)}")
    events = [{"type": "click", "pos": [3, 4]}, {"type": "key", "key": "a"}, {"type": "key", "key": "Enter"},
              {"type": "scroll", "dy": -3, "dx": 0}, {"type": "resize"}, ["not", "dict"]]
    print("매핑 패턴:", [handle_event(e) for e in events])
    shapes = [Circle(Point(0, 0), 3), Circle(Point(5, 5), 20), Circle(Point(1, 1), 2),
              Rect(Point(0, 0), 4, 4), Rect(Point(1, 2), 3, 5), Point(7, 8), 2.5, "x"]
    for s in shapes:
        print("클래스 패턴:", describe(s))
    print("값 패턴 함정:", value_pattern_trap("blue"))
    print("계산기:", evaluate(("+", 2, ("*", 3, ("-", 4)))))
    assert evaluate(("+", 2, ("*", 3, ("-", 4)))) == -10
    print("__match_args__:", Circle.__match_args__)
    print("모든 검증 통과")
