"""전략 패턴: 알고리즘군을 정의하고 각각 캡슐화해 실행 중에 바꿔 끼운다.

python strategy.py 로 실행하면 검증과 예제 출력이 나온다.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable


@dataclass
class Item:
    name: str
    price: int
    qty: int


# 1. 클래스 전략
class ShippingStrategy(ABC):
    @abstractmethod
    def cost(self, items: list[Item]) -> int: ...


class FlatRate(ShippingStrategy):
    def __init__(self, fee=3000): self.fee = fee
    def cost(self, items): return self.fee


class FreeOver(ShippingStrategy):
    def __init__(self, threshold=40_000, fee=3000): self.threshold, self.fee = threshold, fee
    def cost(self, items):
        return 0 if sum(i.price * i.qty for i in items) >= self.threshold else self.fee


class PerItem(ShippingStrategy):
    def __init__(self, unit=1000): self.unit = unit
    def cost(self, items): return self.unit * sum(i.qty for i in items)


class Cart:                                         # Context
    def __init__(self, shipping: ShippingStrategy):
        self.items: list[Item] = []
        self.shipping = shipping                    # 실행 중에 바꿔 끼울 수 있다

    def total(self):
        return sum(i.price * i.qty for i in self.items) + self.shipping.cost(self.items)


# 2. 함수 전략: 메서드가 하나뿐인 전략은 함수로 충분하다
PriceRule = Callable[[int], int]

RULES: dict[str, PriceRule] = {
    "none": lambda p: p,
    "member": lambda p: p * 95 // 100,
    "coupon5000": lambda p: max(0, p - 5000),
}


def checkout(price: int, rule: PriceRule) -> int:
    return rule(price)


if __name__ == "__main__":
    items = [Item("book", 18_000, 2), Item("pen", 1_500, 4)]
    cart = Cart(FlatRate())
    cart.items = items
    results = {}
    for s in [FlatRate(), FreeOver(), PerItem()]:
        cart.shipping = s
        results[type(s).__name__] = cart.total()
    print("배송 전략별 합계:", results)
    assert results == {"FlatRate": 45_000, "FreeOver": 42_000, "PerItem": 48_000}

    cart.items = [Item("laptop", 1_200_000, 1)]
    cart.shipping = FreeOver()
    assert cart.total() == 1_200_000

    print("가격 규칙별:", {k: checkout(30_000, r) for k, r in RULES.items()})
    assert [checkout(30_000, r) for r in RULES.values()] == [30_000, 28_500, 25_000]

    # 표준 라이브러리의 전략: sorted의 key 함수
    words = ["banana", "apple", "Cherry", "date"]
    print("key=None      :", sorted(words))
    print("key=str.lower :", sorted(words, key=str.lower))
    print("key=len       :", sorted(words, key=len))
    assert sorted(words) == ["Cherry", "apple", "banana", "date"]
    assert sorted(words, key=str.lower) == ["apple", "banana", "Cherry", "date"]
    print("모든 검증 통과")
