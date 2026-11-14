"""책임 연쇄 패턴: 요청을 처리할 수 있는 객체가 나올 때까지 처리기 사슬을 따라 넘긴다.

python chain_of_responsibility.py 로 실행하면 검증과 예제 출력이 나온다.
"""
from __future__ import annotations
from abc import ABC
from typing import Callable


# 1. 고전 형태: 각 처리기가 다음 처리기를 참조한다 (고객 문의 등급 처리)
class Handler(ABC):
    def __init__(self): self._next: Handler | None = None

    def set_next(self, h: Handler) -> Handler:
        self._next = h
        return h                                   # a.set_next(b).set_next(c) 체이닝

    def handle(self, amount: int) -> str:
        if self._next:
            return self._next.handle(amount)
        return f"{amount}원: 처리할 수 있는 사람이 없음"


class TeamLead(Handler):
    def handle(self, amount):
        return f"{amount}원: 팀장 승인" if amount <= 100_000 else super().handle(amount)


class Manager(Handler):
    def handle(self, amount):
        return f"{amount}원: 부장 승인" if amount <= 1_000_000 else super().handle(amount)


class Director(Handler):
    def handle(self, amount):
        return f"{amount}원: 이사 승인" if amount <= 10_000_000 else super().handle(amount)


# 2. 미들웨어 형태: 모든 처리기가 요청을 보고, 다음으로 넘길지 스스로 정한다
Request = dict
Response = dict
App = Callable[[Request], Response]


def auth_middleware(next_app: App) -> App:
    def app(req):
        if req.get("token") != "secret":
            return {"status": 401, "body": "unauthorized"}     # 여기서 사슬을 끊는다
        req["user"] = "kim"
        return next_app(req)
    return app


def logging_middleware(log: list) -> Callable[[App], App]:
    def mw(next_app: App) -> App:
        def app(req):
            log.append(f"-> {req['path']}")
            res = next_app(req)
            log.append(f"<- {res['status']}")                   # 응답은 역순으로 지나간다
            return res
        return app
    return mw


def view(req):
    return {"status": 200, "body": f"hello {req['user']}"}


def build(app: App, middlewares) -> App:
    for mw in reversed(middlewares):                # 리스트 앞쪽이 가장 바깥
        app = mw(app)
    return app


if __name__ == "__main__":
    chain = TeamLead()
    chain.set_next(Manager()).set_next(Director())
    cases = [50_000, 700_000, 5_000_000, 50_000_000]
    results = [chain.handle(a) for a in cases]
    for r in results:
        print(r)
    assert ["팀장" in results[0], "부장" in results[1], "이사" in results[2], "없음" in results[3]] == [True] * 4

    log: list = []
    app = build(view, [logging_middleware(log), auth_middleware])
    ok = app({"path": "/me", "token": "secret"})
    bad = app({"path": "/me", "token": "x"})
    print(ok, bad)
    print(log)
    assert ok == {"status": 200, "body": "hello kim"} and bad["status"] == 401
    assert log == ["-> /me", "<- 200", "-> /me", "<- 401"]
    print("모든 검증 통과")
