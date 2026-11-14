"""커맨드 패턴: 요청을 객체로 만들어 저장·취소·재실행·조합할 수 있게 한다.

python command.py 로 실행하면 무작위 실행 취소 검증과 예제 출력이 나온다.
"""
from abc import ABC, abstractmethod
import random


class Editor:                                        # Receiver: 실제 일을 하는 객체
    def __init__(self): self.text = ""


class Command(ABC):
    @abstractmethod
    def execute(self) -> None: ...

    @abstractmethod
    def undo(self) -> None: ...


class Insert(Command):
    def __init__(self, ed: Editor, pos: int, s: str):
        self.ed, self.pos, self.s = ed, pos, s

    def execute(self):
        t = self.ed.text
        self.ed.text = t[:self.pos] + self.s + t[self.pos:]

    def undo(self):
        t = self.ed.text
        self.ed.text = t[:self.pos] + t[self.pos + len(self.s):]


class Delete(Command):
    def __init__(self, ed: Editor, pos: int, n: int):
        self.ed, self.pos, self.n = ed, pos, n
        self.removed = ""                            # undo에 필요한 정보를 실행 때 저장

    def execute(self):
        t = self.ed.text
        self.removed = t[self.pos:self.pos + self.n]
        self.ed.text = t[:self.pos] + t[self.pos + self.n:]

    def undo(self):
        t = self.ed.text
        self.ed.text = t[:self.pos] + self.removed + t[self.pos:]


class Macro(Command):                                # 커맨드 여러 개를 하나로 (컴포지트)
    def __init__(self, cmds: list[Command]): self.cmds = cmds
    def execute(self):
        for c in self.cmds: c.execute()
    def undo(self):
        for c in reversed(self.cmds): c.undo()


class History:                                       # Invoker: 실행하고 기록한다
    def __init__(self):
        self.done: list[Command] = []
        self.undone: list[Command] = []

    def run(self, cmd: Command):
        cmd.execute()
        self.done.append(cmd)
        self.undone.clear()                          # 새 명령을 실행하면 redo 기록은 버린다

    def undo(self):
        if self.done:
            c = self.done.pop()
            c.undo()
            self.undone.append(c)

    def redo(self):
        if self.undone:
            c = self.undone.pop()
            c.execute()
            self.done.append(c)


if __name__ == "__main__":
    ed, h = Editor(), History()
    h.run(Insert(ed, 0, "Hello"))
    h.run(Insert(ed, 5, " World"))
    h.run(Delete(ed, 0, 6))
    print("실행 후:", repr(ed.text))
    h.undo(); print("undo 1:", repr(ed.text))
    h.undo(); print("undo 2:", repr(ed.text))
    h.redo(); print("redo  :", repr(ed.text))
    assert ed.text == "Hello World"

    h.run(Macro([Insert(ed, 0, "["), Insert(ed, 12, "]")]))
    print("매크로:", repr(ed.text))
    h.undo()
    assert ed.text == "Hello World"

    # 무작위 검증: 명령을 실행하며 텍스트 스냅숏을 남기고, undo로 역순 복원되는지 확인
    rng = random.Random(7)
    for _ in range(300):
        ed, h, snaps = Editor(), History(), []
        for _ in range(rng.randint(1, 30)):
            snaps.append(ed.text)
            if ed.text and rng.random() < 0.4:
                p = rng.randrange(len(ed.text))
                h.run(Delete(ed, p, rng.randint(1, 4)))
            else:
                h.run(Insert(ed, rng.randint(0, len(ed.text)), rng.choice(["a", "bc", "def"])))
        final = ed.text
        for s in reversed(snaps):
            h.undo()
            assert ed.text == s
        for _ in snaps:
            h.redo()
        assert ed.text == final
    print("무작위 300회: undo로 모든 중간 상태 복원, redo로 최종 상태 복원")
    print("모든 검증 통과")
