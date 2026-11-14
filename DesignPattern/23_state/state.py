"""상태 패턴: 상태마다 클래스를 두고, 객체의 행동을 현재 상태 객체에 위임한다.

python state.py 로 실행하면 조건문 버전과의 무작위 비교 검증이 나온다.
"""
from __future__ import annotations
from abc import ABC
import random


class InvalidTransition(Exception):
    pass


# 상태 패턴 버전 -------------------------------------------------------------
class OrderState(ABC):
    name = "?"

    def pay(self, o: Order):     raise InvalidTransition(f"{self.name}: pay 불가")
    def ship(self, o: Order):    raise InvalidTransition(f"{self.name}: ship 불가")
    def deliver(self, o: Order): raise InvalidTransition(f"{self.name}: deliver 불가")
    def cancel(self, o: Order):  raise InvalidTransition(f"{self.name}: cancel 불가")


class Pending(OrderState):
    name = "PENDING"
    def pay(self, o): o.state = Paid()
    def cancel(self, o): o.state = Cancelled()


class Paid(OrderState):
    name = "PAID"
    def ship(self, o): o.state = Shipped()
    def cancel(self, o):
        o.refunded = True                          # 상태별 부수 효과도 그 상태 클래스에
        o.state = Cancelled()


class Shipped(OrderState):
    name = "SHIPPED"
    def deliver(self, o): o.state = Delivered()


class Delivered(OrderState):
    name = "DELIVERED"


class Cancelled(OrderState):
    name = "CANCELLED"


class Order:                                       # Context
    def __init__(self):
        self.state: OrderState = Pending()
        self.refunded = False

    def pay(self): self.state.pay(self)
    def ship(self): self.state.ship(self)
    def deliver(self): self.state.deliver(self)
    def cancel(self): self.state.cancel(self)


# 비교: 조건문 버전 ------------------------------------------------------------
class OrderIf:
    def __init__(self):
        self.state = "PENDING"
        self.refunded = False

    def act(self, action):
        s = self.state
        if action == "pay" and s == "PENDING":
            self.state = "PAID"
        elif action == "ship" and s == "PAID":
            self.state = "SHIPPED"
        elif action == "deliver" and s == "SHIPPED":
            self.state = "DELIVERED"
        elif action == "cancel" and s == "PENDING":
            self.state = "CANCELLED"
        elif action == "cancel" and s == "PAID":
            self.refunded = True
            self.state = "CANCELLED"
        else:
            raise InvalidTransition(f"{s}: {action} 불가")


# 변형: 전이 표 (상태 x 이벤트 -> 다음 상태). 상태별 행동이 단순할 때 가장 짧다
TABLE = {
    ("PENDING", "pay"): "PAID",
    ("PENDING", "cancel"): "CANCELLED",
    ("PAID", "ship"): "SHIPPED",
    ("PAID", "cancel"): "CANCELLED",
    ("SHIPPED", "deliver"): "DELIVERED",
}


if __name__ == "__main__":
    o = Order()
    trace = [o.state.name]
    for act in ["pay", "ship", "deliver"]:
        getattr(o, act)()
        trace.append(o.state.name)
    print(" -> ".join(trace))
    try:
        o.cancel()
    except InvalidTransition as e:
        print("잘못된 전이:", e)

    o2 = Order(); o2.pay(); o2.cancel()
    assert o2.state.name == "CANCELLED" and o2.refunded

    rng = random.Random(2)
    actions = ["pay", "ship", "deliver", "cancel"]
    for _ in range(2000):
        a, b, state = Order(), OrderIf(), "PENDING"
        for _ in range(rng.randint(1, 8)):
            act = rng.choice(actions)
            ra = rb = rt = "ok"
            try: getattr(a, act)()
            except InvalidTransition: ra = "err"
            try: b.act(act)
            except InvalidTransition: rb = "err"
            nxt = TABLE.get((state, act))
            if nxt: state = nxt
            else: rt = "err"
            assert ra == rb == rt and a.state.name == b.state == state and a.refunded == b.refunded
    print("무작위 동작열 2000개: 상태 패턴 = 조건문 버전 = 전이 표")
    print("모든 검증 통과")
