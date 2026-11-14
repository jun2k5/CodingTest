"""중재자 패턴: 객체끼리 직접 참조하지 않고 중재자를 통해서만 소통하게 한다.

python mediator.py 로 실행하면 검증과 예제 출력이 나온다.
"""
from __future__ import annotations


# 예 1: 회원가입 폼. 위젯들은 서로를 모르고 중재자에게 '바뀌었다'고만 알린다
class Widget:
    def __init__(self, name: str, form: SignupForm):
        self.name, self.form = name, form
        self.enabled = True

    def changed(self):
        self.form.notify(self)


class TextField(Widget):
    def __init__(self, name, form):
        super().__init__(name, form)
        self.value = ""

    def type(self, text):
        self.value = text
        self.changed()


class Checkbox(Widget):
    def __init__(self, name, form):
        super().__init__(name, form)
        self.checked = False

    def toggle(self):
        self.checked = not self.checked
        self.changed()


class Button(Widget):
    pass


class SignupForm:                                   # Concrete Mediator: 상호작용 규칙이 여기에만 있다
    def __init__(self):
        self.email = TextField("email", self)
        self.company = TextField("company", self)
        self.is_business = Checkbox("is_business", self)
        self.submit = Button("submit", self)
        self.company.enabled = False
        self.submit.enabled = False
        self.events: list[str] = []

    def notify(self, sender: Widget):
        self.events.append(sender.name)
        if sender is self.is_business:
            self.company.enabled = self.is_business.checked
            if not self.is_business.checked:
                self.company.value = ""
        valid = "@" in self.email.value and (not self.is_business.checked or bool(self.company.value))
        self.submit.enabled = valid


# 예 2: 채팅방. 사용자 N명이 서로를 직접 알면 연결이 N(N-1)/2개 필요하다
class ChatRoom:
    def __init__(self): self.users: dict[str, User] = {}

    def join(self, user: User):
        self.users[user.name] = user
        user.room = self

    def send(self, sender: str, text: str, to: str | None = None):
        targets = [self.users[to]] if to else [u for n, u in self.users.items() if n != sender]
        for u in targets:
            u.inbox.append(f"{sender}: {text}")


class User:
    def __init__(self, name):
        self.name, self.room, self.inbox = name, None, []

    def say(self, text, to=None):
        self.room.send(self.name, text, to)


if __name__ == "__main__":
    f = SignupForm()
    f.email.type("kim@example.com")
    print("이메일 입력 후 제출 가능:", f.submit.enabled)
    assert f.submit.enabled
    f.is_business.toggle()
    print("사업자 체크 후 회사명 입력 가능:", f.company.enabled, "| 제출 가능:", f.submit.enabled)
    assert f.company.enabled and not f.submit.enabled
    f.company.type("ACME")
    assert f.submit.enabled
    f.is_business.toggle()
    assert not f.company.enabled and f.company.value == "" and f.submit.enabled
    print("이벤트 순서:", f.events)

    room = ChatRoom()
    a, b, c = User("a"), User("b"), User("c")
    for u in (a, b, c):
        room.join(u)
    a.say("hi")
    c.say("only b", to="b")
    print("b inbox:", b.inbox)
    assert b.inbox == ["a: hi", "c: only b"] and c.inbox == ["a: hi"] and a.inbox == []

    for n in (5, 10, 50):
        print(f"사용자 {n}명: 직접 연결 {n * (n - 1) // 2}개 vs 중재자 연결 {n}개")
    print("모든 검증 통과")
