"""MVC · MVP · MVVM을 같은 할 일 목록 기능으로 비교한다.

python mvc.py 로 실행하면 검증과 예제 출력이 나온다.
"""
from __future__ import annotations
from typing import Callable


# 공통 Model: 데이터와 규칙만 안다. 화면은 모른다 -----------------------------------
class TodoModel:
    def __init__(self):
        self.items: list[dict] = []
        self._listeners: list[Callable] = []

    def on_change(self, fn): self._listeners.append(fn)

    def _changed(self):
        for fn in self._listeners: fn()

    def add(self, title: str):
        title = title.strip()
        if not title:
            raise ValueError("제목이 비었다")
        self.items.append({"title": title, "done": False})
        self._changed()

    def toggle(self, idx: int):
        self.items[idx]["done"] = not self.items[idx]["done"]
        self._changed()

    def remaining(self): return sum(not t["done"] for t in self.items)


# 1. MVC: View는 Model을 관찰해 스스로 다시 그린다. Controller는 입력을 Model 호출로 바꾼다
class MvcView:
    def __init__(self, model: TodoModel):
        self.model, self.screen = model, ""
        model.on_change(self.render)                     # View -> Model 관찰

    def render(self):
        lines = [f"[{'x' if t['done'] else ' '}] {t['title']}" for t in self.model.items]
        self.screen = "\n".join(lines + [f"남은 일: {self.model.remaining()}"])


class MvcController:
    def __init__(self, model: TodoModel): self.model = model

    def handle(self, command: str):                      # 사용자 입력 해석
        if command.startswith("add "):
            self.model.add(command[4:])
        elif command.startswith("done "):
            self.model.toggle(int(command[5:]))


# 2. MVP: View는 수동적(Passive View). Presenter가 Model을 읽어 View에 값을 밀어 넣는다
class FakeMvpView:
    """실제로는 GUI 위젯. 여기선 Presenter가 넣어 준 값을 기록만 한다."""
    def __init__(self): self.lines, self.counter, self.error = [], "", ""
    def show_items(self, lines): self.lines = lines
    def show_counter(self, text): self.counter = text
    def show_error(self, msg): self.error = msg


class TodoPresenter:
    def __init__(self, model: TodoModel, view: FakeMvpView):
        self.model, self.view = model, view

    def on_add_clicked(self, text: str):
        try:
            self.model.add(text)
            self.view.show_error("")
        except ValueError as e:
            self.view.show_error(str(e))
        self._refresh()

    def on_item_clicked(self, idx: int):
        self.model.toggle(idx)
        self._refresh()

    def _refresh(self):
        self.view.show_items([("✔ " if t["done"] else "· ") + t["title"] for t in self.model.items])
        self.view.show_counter(f"{self.model.remaining()}개 남음")


# 3. MVVM: ViewModel이 화면 상태를 '관찰 가능한 속성'으로 노출하고, View는 바인딩만 한다
class Observable:
    def __init__(self, value):
        self._value, self._subs = value, []
    def bind(self, fn):
        self._subs.append(fn); fn(self._value)
    def set(self, v):
        self._value = v
        for fn in self._subs: fn(v)
    def get(self): return self._value


class TodoViewModel:
    def __init__(self, model: TodoModel):
        self.model = model
        self.new_title = Observable("")                  # 입력창과 양방향 바인딩될 값
        self.can_add = Observable(False)
        self.summary = Observable("0개 남음")
        self.new_title.bind(lambda v: self.can_add.set(bool(v.strip())))
        model.on_change(lambda: self.summary.set(f"{model.remaining()}개 남음"))

    def add(self):                                       # 버튼의 Command 바인딩
        if self.can_add.get():
            self.model.add(self.new_title.get())
            self.new_title.set("")


if __name__ == "__main__":
    m = TodoModel()
    view, ctrl = MvcView(m), MvcController(m)
    for cmd in ["add 장보기", "add 운동", "done 0"]:
        ctrl.handle(cmd)
    print("[MVC]\n" + view.screen)
    assert view.screen.endswith("남은 일: 1")

    m2, fv = TodoModel(), FakeMvpView()
    p = TodoPresenter(m2, fv)
    p.on_add_clicked("   ")
    assert fv.error == "제목이 비었다"
    p.on_add_clicked("책 읽기"); p.on_item_clicked(0)
    print("[MVP]", fv.lines, fv.counter, repr(fv.error))
    assert fv.lines == ["✔ 책 읽기"] and fv.counter == "0개 남음" and fv.error == ""

    m3 = TodoModel()
    vm = TodoViewModel(m3)
    button_enabled = []
    vm.can_add.bind(button_enabled.append)               # View 쪽 바인딩: 버튼 활성 상태
    vm.add()                                              # 비어 있으면 아무 일도 없다
    vm.new_title.set("코드 리뷰")
    vm.add()
    print("[MVVM] 버튼 활성 변화:", button_enabled, "| summary:", vm.summary.get(), "| 입력창:", repr(vm.new_title.get()))
    assert len(m3.items) == 1 and vm.summary.get() == "1개 남음" and button_enabled == [False, True, False]
    print("모든 검증 통과")
