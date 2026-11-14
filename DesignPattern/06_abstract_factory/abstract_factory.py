"""추상 팩토리 패턴: 서로 관련된 객체 묶음(제품군)을 구체 클래스 없이 만든다.

python abstract_factory.py 로 실행하면 검증과 예제 출력이 나온다.
"""
from abc import ABC, abstractmethod


# 추상 제품 A, B
class Button(ABC):
    @abstractmethod
    def render(self, label: str) -> str: ...


class TextBox(ABC):
    @abstractmethod
    def render(self, value: str) -> str: ...


# 제품군 1: 라이트 테마
class LightButton(Button):
    family = "light"
    def render(self, label): return f"[ {label} ] (흰 배경)"


class LightTextBox(TextBox):
    family = "light"
    def render(self, value): return f"|{value:<10}| (검은 글씨)"


# 제품군 2: 다크 테마
class DarkButton(Button):
    family = "dark"
    def render(self, label): return f"[ {label} ] (검은 배경)"


class DarkTextBox(TextBox):
    family = "dark"
    def render(self, value): return f"|{value:<10}| (흰 글씨)"


# 추상 팩토리: 제품군 하나를 통째로 만든다
class UIFactory(ABC):
    @abstractmethod
    def create_button(self) -> Button: ...

    @abstractmethod
    def create_textbox(self) -> TextBox: ...


class LightFactory(UIFactory):
    def create_button(self): return LightButton()
    def create_textbox(self): return LightTextBox()


class DarkFactory(UIFactory):
    def create_button(self): return DarkButton()
    def create_textbox(self): return DarkTextBox()


# 클라이언트: 팩토리만 알고 구체 제품은 모른다
class LoginForm:
    def __init__(self, factory: UIFactory):
        self.user = factory.create_textbox()
        self.submit = factory.create_button()

    def render(self) -> list[str]:
        return [self.user.render("id"), self.submit.render("로그인")]


FACTORIES = {"light": LightFactory, "dark": DarkFactory}


if __name__ == "__main__":
    for name, F in FACTORIES.items():
        form = LoginForm(F())
        print(name, form.render())
        # 한 팩토리에서 나온 제품은 항상 같은 제품군이다
        assert form.user.family == form.submit.family == name

    # 팩토리 없이 직접 만들면 제품군이 섞일 수 있다
    mixed = [LightTextBox(), DarkButton()]
    assert mixed[0].family != mixed[1].family
    print("직접 생성 시 섞인 조합:", [type(x).__name__ for x in mixed])
    print("모든 검증 통과")
