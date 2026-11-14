"""옵저버 패턴: 한 객체의 상태가 바뀌면 의존하는 객체들에 자동으로 알린다.

python observer.py 로 실행하면 검증과 예제 출력이 나온다.
"""
from __future__ import annotations
from collections import defaultdict
from typing import Callable, Protocol
import gc
import weakref


# 1. 고전 형태 (푸시 모델): Subject가 바뀐 값을 넘겨준다
class Observer(Protocol):
    def update(self, symbol: str, price: float) -> None: ...


class Stock:                                        # Subject
    def __init__(self, symbol, price):
        self.symbol, self._price = symbol, price
        self._observers: list[Observer] = []

    def attach(self, o: Observer): self._observers.append(o)
    def detach(self, o: Observer): self._observers.remove(o)

    @property
    def price(self): return self._price

    @price.setter
    def price(self, v):
        if v != self._price:                        # 실제로 바뀔 때만 알린다
            self._price = v
            for o in list(self._observers):         # 알림 도중 detach돼도 안전하게 복사본 순회
                o.update(self.symbol, v)


class PriceDisplay:
    def __init__(self): self.lines = []
    def update(self, symbol, price): self.lines.append(f"{symbol} {price}")


class Alert:
    def __init__(self, limit): self.limit, self.fired = limit, []
    def update(self, symbol, price):
        if price >= self.limit:
            self.fired.append(price)


# 2. 이벤트 버스: 이벤트 이름으로 구독. 발행자와 구독자가 서로를 모른다
class EventBus:
    def __init__(self): self._subs: dict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, event: str, fn: Callable):
        self._subs[event].append(fn)
        return lambda: self._subs[event].remove(fn)     # 구독 해제 함수

    def publish(self, event: str, **payload):
        for fn in list(self._subs[event]):
            fn(**payload)


# 3. 약한 참조 옵저버: 구독자가 사라지면 자동으로 목록에서 빠진다 (메모리 누수 방지)
class WeakSubject:
    def __init__(self): self._obs = weakref.WeakSet()
    def attach(self, o): self._obs.add(o)
    def notify(self, v):
        for o in list(self._obs):
            o.update("W", v)
    def count(self): return len(self._obs)


if __name__ == "__main__":
    s = Stock("ACME", 100)
    disp, alert = PriceDisplay(), Alert(110)
    s.attach(disp); s.attach(alert)
    for p in [101, 101, 108, 112, 115]:
        s.price = p
    s.detach(alert)
    s.price = 120
    print("display:", disp.lines)
    print("alert  :", alert.fired)
    assert disp.lines == ["ACME 101", "ACME 108", "ACME 112", "ACME 115", "ACME 120"]
    assert alert.fired == [112, 115]                # detach 뒤 120은 받지 않는다

    bus, sent, points = EventBus(), [], {}
    bus.subscribe("user.signup", lambda email, **_: sent.append(f"welcome {email}"))
    off = bus.subscribe("user.signup", lambda email, **_: points.__setitem__(email, 1000))
    bus.publish("user.signup", email="kim@example.com")
    off()
    bus.publish("user.signup", email="lee@example.com")
    print("이벤트 버스:", sent, points)
    assert sent == ["welcome kim@example.com", "welcome lee@example.com"]
    assert points == {"kim@example.com": 1000}

    ws = WeakSubject()
    tmp = PriceDisplay()
    ws.attach(tmp)
    assert ws.count() == 1
    del tmp
    gc.collect()
    print("약한 참조: 구독자 삭제 후 남은 구독자 수 =", ws.count())
    assert ws.count() == 0
    print("모든 검증 통과")
