"""객체지향 4대 특성과 합성 vs 상속.

python oop_principles.py 로 실행하면 검증과 예제 출력이 나온다.
"""
from abc import ABC, abstractmethod
import math


# 1. 캡슐화: 상태는 숨기고, 규칙을 지키는 메서드로만 바꾼다
class Account:
    def __init__(self, owner: str, balance: int = 0):
        self.owner = owner
        self._balance = balance          # 밖에서 직접 바꾸지 않는다는 약속

    @property
    def balance(self) -> int:           # 읽기만 공개
        return self._balance

    def deposit(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("입금액은 양수")
        self._balance += amount

    def withdraw(self, amount: int) -> None:
        if amount > self._balance:
            raise ValueError("잔액 부족")
        self._balance -= amount


# 2. 추상화 + 4. 다형성: 호출하는 쪽은 Shape만 안다
class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...


class Circle(Shape):
    def __init__(self, r): self.r = r
    def area(self): return math.pi * self.r ** 2


class Rect(Shape):
    def __init__(self, w, h): self.w, self.h = w, h
    def area(self): return self.w * self.h


def total_area(shapes: list[Shape]) -> float:
    return sum(s.area() for s in shapes)     # 도형 종류가 늘어도 이 함수는 그대로


# 3. 상속의 함정: 부모의 내부 구현에 의존하게 된다 (깨지기 쉬운 기반 클래스)
class Bag:
    def __init__(self): self._items = []
    def add(self, x): self._items.append(x)
    def add_all(self, xs):
        for x in xs:
            self.add(x)                     # 내부에서 add를 다시 부른다
    def __len__(self): return len(self._items)


class CountingBagInherit(Bag):
    """상속으로 '추가 시도 횟수'를 센다."""
    def __init__(self):
        super().__init__()
        self.add_count = 0
    def add(self, x):
        self.add_count += 1
        super().add(x)
    def add_all(self, xs):
        self.add_count += len(xs)           # 여기서 세고
        super().add_all(xs)                 # 부모가 add를 불러 또 센다


class CountingBagCompose:
    """합성으로 같은 기능을 만든다. Bag을 '가지고' 공개 메서드만 쓴다."""
    def __init__(self, bag: Bag):
        self._bag = bag
        self.add_count = 0
    def add(self, x):
        self.add_count += 1
        self._bag.add(x)
    def add_all(self, xs):
        self.add_count += len(xs)
        for x in xs:
            self._bag.add(x)                # 감싼 객체의 add를 직접 부른다
    def __len__(self): return len(self._bag)


if __name__ == "__main__":
    acc = Account("kim", 1000)
    acc.deposit(500)
    acc.withdraw(300)
    assert acc.balance == 1200
    try:
        acc.withdraw(10_000)
        raise AssertionError("잔액 부족 예외가 나야 한다")
    except ValueError:
        pass
    try:
        acc.balance = 0
        raise AssertionError("balance는 읽기 전용이어야 한다")
    except AttributeError:
        pass
    print("캡슐화: 잔액", acc.balance, "| 직접 대입 시 AttributeError")

    shapes = [Circle(1), Rect(2, 3), Circle(2)]
    assert abs(total_area(shapes) - (math.pi + 6 + 4 * math.pi)) < 1e-9
    print(f"다형성: total_area = {total_area(shapes):.4f}")

    a = CountingBagInherit()
    a.add_all(["x", "y", "z"])
    b = CountingBagCompose(Bag())
    b.add_all(["x", "y", "z"])
    print(f"상속 버전 add_count = {a.add_count} (실제 원소 {len(a)}개)")
    print(f"합성 버전 add_count = {b.add_count} (실제 원소 {len(b)}개)")
    assert a.add_count == 6 and len(a) == 3     # 두 번 셌다
    assert b.add_count == 3 and len(b) == 3
    print("모든 검증 통과")
