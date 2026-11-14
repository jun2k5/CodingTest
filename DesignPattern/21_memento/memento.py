"""메멘토 패턴: 캡슐화를 깨지 않고 객체의 내부 상태를 저장했다가 복원한다.

python memento.py 로 실행하면 무작위 복원 검증과 예제 출력이 나온다.
"""
from __future__ import annotations
import copy
import random


class Memento:
    """Originator만 내용을 해석한다. Caretaker에게는 불투명한 상자다."""
    __slots__ = ("_state", "label")

    def __init__(self, state, label: str):
        self._state = state
        self.label = label                         # 바깥에 보여 줘도 되는 정보만 공개


class Game:                                        # Originator
    def __init__(self):
        self._level = 1
        self._hp = 100
        self._inventory: list[str] = []

    def play(self, rng: random.Random):
        self._hp -= rng.randint(0, 40)
        if rng.random() < 0.5:
            self._inventory.append(rng.choice(["potion", "sword", "key"]))
        if self._hp <= 0:
            self._hp, self._level = 100, 1         # 죽으면 처음부터
        else:
            self._level += 1

    def save(self) -> Memento:
        state = (self._level, self._hp, copy.deepcopy(self._inventory))
        return Memento(state, f"Lv{self._level} HP{self._hp}")

    def restore(self, m: Memento):
        lv, hp, inv = m._state
        self._level, self._hp, self._inventory = lv, hp, copy.deepcopy(inv)

    def status(self):
        return (self._level, self._hp, tuple(self._inventory))


class SaveSlots:                                   # Caretaker: 저장·보관만, 내용은 모른다
    def __init__(self, limit=3):
        self.slots: list[Memento] = []
        self.limit = limit

    def push(self, m: Memento):
        self.slots.append(m)
        if len(self.slots) > self.limit:           # 오래된 저장은 버린다 (메모리 제한)
            self.slots.pop(0)

    def pop(self) -> Memento:
        return self.slots.pop()


if __name__ == "__main__":
    rng = random.Random(11)
    g, slots = Game(), SaveSlots()
    for _ in range(3):
        g.play(rng)
    slots.push(g.save())
    before = g.status()
    print("저장:", slots.slots[-1].label, before)
    for _ in range(4):
        g.play(rng)
    print("진행 후:", g.status())
    g.restore(slots.pop())
    print("복원:", g.status())
    assert g.status() == before

    # 저장 뒤 원본 리스트를 바꿔도 메멘토는 영향받지 않아야 한다 (깊은 복사)
    g._inventory.append("cheat")
    m = g.save()
    g._inventory.clear()
    g.restore(m)
    assert "cheat" in g.status()[2]

    rng = random.Random(0)
    for _ in range(300):
        g, slots, snaps = Game(), SaveSlots(limit=5), []
        for _ in range(rng.randint(1, 20)):
            g.play(rng)
            if rng.random() < 0.5:
                slots.push(g.save())
                snaps.append(g.status())
        for expected in reversed(snaps[-5:]):
            g.play(rng)
            g.restore(slots.pop())
            assert g.status() == expected
    print("무작위 300회: 최근 5개 저장 지점으로 정확히 복원")
    print("모든 검증 통과")
