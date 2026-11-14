"""의존성 주입(DI)과 IoC 컨테이너.

python dependency_injection.py 로 실행하면 검증과 예제 출력이 나온다.
"""
from __future__ import annotations
import inspect
from typing import Callable, Protocol, get_type_hints


# 역할(인터페이스)
class UserRepo(Protocol):
    def get(self, uid: int) -> dict | None: ...


class Mailer(Protocol):
    def send(self, to: str, body: str) -> None: ...


# 구현
class InMemoryUserRepo:
    def __init__(self):
        self.rows = {1: {"id": 1, "email": "kim@example.com"}}
    def get(self, uid): return self.rows.get(uid)


class ConsoleMailer:
    def __init__(self): self.sent = []
    def send(self, to, body): self.sent.append((to, body))


# 1. 주입 없음: 서비스가 직접 구현체를 만든다 -> 바꿔 끼우기·테스트가 어렵다
class WelcomeServiceHardwired:
    def __init__(self):
        self.repo = InMemoryUserRepo()
        self.mailer = ConsoleMailer()


# 2. 생성자 주입: 필요한 것을 밖에서 받는다 (가장 권장되는 형태)
class WelcomeService:
    def __init__(self, repo: UserRepo, mailer: Mailer):
        self.repo, self.mailer = repo, mailer

    def welcome(self, uid: int) -> bool:
        user = self.repo.get(uid)
        if not user:
            return False
        self.mailer.send(user["email"], "환영합니다")
        return True


# 3. 아주 작은 IoC 컨테이너: 등록된 규칙대로 객체 그래프를 조립한다
class Container:
    def __init__(self):
        self._providers: dict[type, tuple[Callable, bool]] = {}
        self._singletons: dict[type, object] = {}
        self._resolving: list[type] = []

    def register(self, key: type, provider: Callable | None = None, singleton=False):
        self._providers[key] = (provider or key, singleton)

    def resolve(self, key: type):
        if key in self._singletons:
            return self._singletons[key]
        if key in self._resolving:
            chain = " -> ".join(k.__name__ for k in self._resolving + [key])
            raise RuntimeError(f"순환 의존: {chain}")
        provider, singleton = self._providers.get(key, (key, False))
        self._resolving.append(key)
        try:
            obj = self._build(provider)
        finally:
            self._resolving.pop()
        if singleton:
            self._singletons[key] = obj
        return obj

    def _build(self, provider: Callable):
        target = provider.__init__ if inspect.isclass(provider) else provider
        hints = get_type_hints(target)
        params = [p for p in inspect.signature(provider).parameters.values() if p.name in hints]
        kwargs = {p.name: self.resolve(hints[p.name]) for p in params}   # 타입 힌트로 자동 연결
        return provider(**kwargs)


# 4. 비교: 서비스 로케이터. 객체가 스스로 의존성을 '찾아온다' (의존성이 시그니처에 드러나지 않음)
class Locator:
    services: dict[type, object] = {}


class WelcomeServiceLocator:
    def __init__(self):
        self.repo = Locator.services[UserRepo]
        self.mailer = Locator.services[Mailer]


class A:
    def __init__(self, b: B): self.b = b


class B:
    def __init__(self, a: A): self.a = a


if __name__ == "__main__":
    # 테스트에서는 가짜 구현을 직접 넣는다
    class FakeRepo:
        def get(self, uid): return {"id": uid, "email": f"u{uid}@test"} if uid < 10 else None
    fake_mail = ConsoleMailer()
    svc = WelcomeService(FakeRepo(), fake_mail)
    assert svc.welcome(3) and not svc.welcome(99)
    assert fake_mail.sent == [("u3@test", "환영합니다")]
    print("생성자 주입 + 가짜 구현 테스트:", fake_mail.sent)

    c = Container()
    c.register(UserRepo, InMemoryUserRepo, singleton=True)
    c.register(Mailer, ConsoleMailer, singleton=True)
    s1 = c.resolve(WelcomeService)
    s2 = c.resolve(WelcomeService)
    assert s1 is not s2                                # 서비스는 매번 새로 (transient)
    assert s1.repo is s2.repo and s1.mailer is s2.mailer   # 싱글턴으로 등록한 것은 공유
    assert s1.welcome(1)
    print("컨테이너가 조립한 서비스:", type(s1.repo).__name__, type(s1.mailer).__name__, s1.mailer.sent)

    try:
        c.resolve(A)
        raise AssertionError
    except RuntimeError as e:
        print(e)

    print("WelcomeService 시그니처:", inspect.signature(WelcomeService))
    print("WelcomeServiceLocator 시그니처:", inspect.signature(WelcomeServiceLocator))
    print("모든 검증 통과")
