"""SOLID 원칙 예제. 원칙마다 위반 코드와 개선 코드를 둔다.

python solid.py 로 실행하면 검증과 예제 출력이 나온다.
"""
from abc import ABC, abstractmethod
from typing import Protocol


# S: 단일 책임 원칙 -------------------------------------------------------
class ReportBad:
    """계산, 문자열 포맷, 파일 저장을 한 클래스가 모두 한다 (바뀌는 이유가 3개)."""
    def __init__(self, sales): self.sales = sales
    def run(self, path):
        total = sum(self.sales)
        text = f"total={total}"
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return text


class SalesCalculator:
    def total(self, sales): return sum(sales)


class ReportFormatter:
    def format(self, total): return f"total={total}"


class MemoryWriter:                      # 테스트용 저장소. 파일 저장소로 바꿔 끼울 수 있다
    def __init__(self): self.saved = []
    def write(self, text): self.saved.append(text)


# O: 개방-폐쇄 원칙 -------------------------------------------------------
def discount_bad(kind: str, price: int) -> int:
    if kind == "vip":
        return price * 80 // 100
    elif kind == "student":
        return price * 90 // 100
    return price                         # 새 등급이 생기면 이 함수를 고쳐야 한다


class Discount(ABC):
    @abstractmethod
    def apply(self, price: int) -> int: ...


class NoDiscount(Discount):
    def apply(self, price): return price


class RateDiscount(Discount):
    def __init__(self, percent): self.percent = percent
    def apply(self, price): return price * (100 - self.percent) // 100


class FixedDiscount(Discount):           # 기존 코드 수정 없이 추가
    def __init__(self, amount): self.amount = amount
    def apply(self, price): return max(0, price - self.amount)


# L: 리스코프 치환 원칙 ---------------------------------------------------
class Rectangle:
    def __init__(self, w, h): self._w, self._h = w, h
    def set_width(self, w): self._w = w
    def set_height(self, h): self._h = h
    def area(self): return self._w * self._h


class Square(Rectangle):
    """정사각형은 직사각형이다? 너비만 바꿔도 높이가 같이 바뀐다."""
    def __init__(self, s): super().__init__(s, s)
    def set_width(self, w): self._w = self._h = w
    def set_height(self, h): self._w = self._h = h


def stretch(rect: Rectangle) -> int:
    """Rectangle의 계약: 너비와 높이는 따로 바뀐다."""
    rect.set_width(5)
    rect.set_height(4)
    return rect.area()


# I: 인터페이스 분리 원칙 -------------------------------------------------
class Machine(ABC):                      # 뚱뚱한 인터페이스
    @abstractmethod
    def print(self, doc): ...
    @abstractmethod
    def scan(self, doc): ...
    @abstractmethod
    def fax(self, doc): ...


class OldPrinter(Machine):
    def print(self, doc): return f"print {doc}"
    def scan(self, doc): raise NotImplementedError   # 쓰지도 않는 메서드를 구현해야 한다
    def fax(self, doc): raise NotImplementedError


class Printer(Protocol):
    def print(self, doc) -> str: ...


class Scanner(Protocol):
    def scan(self, doc) -> str: ...


class SimplePrinter:                     # 필요한 역할만 구현
    def print(self, doc): return f"print {doc}"


class MultiFunction:
    def print(self, doc): return f"print {doc}"
    def scan(self, doc): return f"scan {doc}"


def print_all(p: Printer, docs): return [p.print(d) for d in docs]


# D: 의존성 역전 원칙 -----------------------------------------------------
class SmtpMailer:
    def send(self, to, msg): raise RuntimeError("실제 메일 서버가 필요하다")


class OrderServiceBad:
    def __init__(self):
        self.mailer = SmtpMailer()       # 구체 클래스를 직접 생성 -> 테스트 불가

    def place(self, user):
        self.mailer.send(user, "주문 완료")


class Notifier(Protocol):
    def send(self, to: str, msg: str) -> None: ...


class OrderService:
    def __init__(self, notifier: Notifier):   # 추상(역할)에 의존, 밖에서 주입
        self.notifier = notifier

    def place(self, user):
        self.notifier.send(user, "주문 완료")


class FakeNotifier:
    def __init__(self): self.sent = []
    def send(self, to, msg): self.sent.append((to, msg))


if __name__ == "__main__":
    # S
    w = MemoryWriter()
    text = ReportFormatter().format(SalesCalculator().total([100, 200, 300]))
    w.write(text)
    assert w.saved == ["total=600"]
    print("SRP: 계산·포맷·저장 분리 ->", w.saved)

    # O
    for kind, d in [("vip", RateDiscount(20)), ("student", RateDiscount(10)), ("none", NoDiscount())]:
        for price in range(0, 10_000, 37):
            assert discount_bad(kind, price) == d.apply(price)
    assert FixedDiscount(3000).apply(10_000) == 7000
    print("OCP: 기존 if-elif와 결과 동일, FixedDiscount는 수정 없이 추가")

    # L
    r, s = Rectangle(1, 1), Square(1)
    print(f"LSP: stretch(Rectangle) = {stretch(r)}, stretch(Square) = {stretch(s)}")
    assert stretch(r) == 20
    assert stretch(s) == 16              # 기대값 20과 다르다 -> 치환 불가

    # I
    assert print_all(SimplePrinter(), ["a", "b"]) == ["print a", "print b"]
    assert print_all(MultiFunction(), ["a"]) == ["print a"]
    try:
        OldPrinter().scan("x")
        raise AssertionError
    except NotImplementedError:
        pass
    print("ISP: Printer 역할만 요구하는 함수는 SimplePrinter·MultiFunction 모두 받는다")

    # D
    try:
        OrderServiceBad().place("kim")
        raise AssertionError
    except RuntimeError as e:
        print("DIP 위반 버전 테스트:", e)
    fake = FakeNotifier()
    OrderService(fake).place("kim")
    assert fake.sent == [("kim", "주문 완료")]
    print("DIP 적용 버전 테스트:", fake.sent)
    print("모든 검증 통과")
