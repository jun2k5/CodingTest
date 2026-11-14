"""자주 보이는 안티패턴과 고친 모습.

python anti_patterns.py 로 실행하면 검증과 예제 출력이 나온다.
"""
import random


# 1. 전역 가변 상태: 테스트 순서에 따라 결과가 달라진다 -------------------------------
_CART: list = []                                    # 모듈 전역 리스트


def add_to_cart_global(item):
    _CART.append(item)
    return len(_CART)


def add_to_cart(cart: list, item):                  # 상태를 인자로 받는다
    cart.append(item)
    return len(cart)


# 2. 매직 넘버·문자열과 긴 if-elif 사슬 -> 표(dict)로 ----------------------------------
def fee_bad(grade, amount):
    if grade == 1:
        return amount * 0.03
    elif grade == 2:
        return amount * 0.02
    elif grade == 3:
        return amount * 0.01
    elif grade == 4:
        return 0
    else:
        return amount * 0.05


FEE_RATE = {"BRONZE": 0.03, "SILVER": 0.02, "GOLD": 0.01, "VIP": 0.0}
DEFAULT_RATE = 0.05
GRADE_CODE = {1: "BRONZE", 2: "SILVER", 3: "GOLD", 4: "VIP"}


def fee(grade: str, amount: int) -> float:
    return amount * FEE_RATE.get(grade, DEFAULT_RATE)


# 3. 신 객체(God Object): 한 클래스가 모든 일을 한다 -------------------------------------
class UserManagerGod:
    def __init__(self):
        self.users, self.logs, self.mails = {}, [], []
    def register(self, email, pw):
        if "@" not in email: raise ValueError("email")
        if len(pw) < 8: raise ValueError("pw")
        self.users[email] = hash(pw)
        self.logs.append(f"register {email}")
        self.mails.append((email, "welcome"))
    # ... 로그인, 비밀번호 변경, 통계, 보고서, 결제 ... 메서드가 계속 늘어난다


class Validator:
    def check(self, email, pw):
        if "@" not in email: raise ValueError("email")
        if len(pw) < 8: raise ValueError("pw")


class UserStore:
    def __init__(self): self.users = {}
    def add(self, email, pw_hash): self.users[email] = pw_hash


class Registration:                                  # 흐름만 조율한다
    def __init__(self, validator, store, mails: list, logs: list):
        self.validator, self.store, self.mails, self.logs = validator, store, mails, logs
    def register(self, email, pw):
        self.validator.check(email, pw)
        self.store.add(email, hash(pw))
        self.logs.append(f"register {email}")
        self.mails.append((email, "welcome"))


# 4. 과설계: 구현이 하나뿐인데 인터페이스·팩토리·전략을 미리 다 만든다 ----------------------
class AbstractGreeterFactory:
    def create(self): return DefaultGreeterStrategyImpl()


class DefaultGreeterStrategyImpl:
    def greet(self, name): return f"hi {name}"


def greet(name): return f"hi {name}"                # 필요해질 때 패턴을 도입해도 늦지 않다


if __name__ == "__main__":
    # 1. 같은 '테스트'를 두 번 돌리면 전역 버전은 결과가 달라진다
    r1 = add_to_cart_global("apple"); r2 = add_to_cart_global("apple")
    print("전역 상태:", r1, r2, "(같은 호출인데 결과가 다르다)")
    assert (r1, r2) == (1, 2)
    assert add_to_cart([], "apple") == add_to_cart([], "apple") == 1

    rng = random.Random(1)
    for _ in range(1000):
        code, amt = rng.randint(0, 5), rng.randint(0, 100_000)
        assert abs(fee_bad(code, amt) - fee(GRADE_CODE.get(code, "?"), amt)) < 1e-9
    print("if-elif 사슬과 표 기반 수수료 계산: 무작위 1000건 일치")

    god = UserManagerGod(); god.register("a@x.com", "password1")
    mails, logs = [], []
    reg = Registration(Validator(), UserStore(), mails, logs)
    reg.register("a@x.com", "password1")
    assert god.mails == mails and god.logs == logs
    print("신 객체 분리: 동작 동일, 책임은 Validator·UserStore·Registration으로 나뉨")

    assert AbstractGreeterFactory().create().greet("kim") == greet("kim")
    print("과설계: 클래스 2개와 함수 1개가 같은 일을 한다")
    print("모든 검증 통과")
