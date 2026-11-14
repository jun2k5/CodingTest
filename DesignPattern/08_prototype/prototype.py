"""프로토타입 패턴: 기존 객체를 복제해 새 객체를 만든다.

python prototype.py 로 실행하면 얕은·깊은 복사 차이와 생성 비용 비교가 나온다.
"""
import copy
import time


class Document:
    def __init__(self, title: str, tags: list[str], style: dict):
        self.title = title
        self.tags = tags
        self.style = style

    def clone(self, deep=True):
        return copy.deepcopy(self) if deep else copy.copy(self)


class Monster:
    """생성 비용이 큰 객체: 만들 때 무거운 계산(맵 로딩 흉내)을 한다."""
    load_count = 0

    def __init__(self, kind: str, hp: int):
        Monster.load_count += 1
        time.sleep(0.01)                             # 무거운 초기화 흉내
        self.kind = kind
        self.hp = hp
        self.skills = ["attack"]
        self.position = (0, 0)

    def __deepcopy__(self, memo):
        # 복제 시에는 무거운 초기화를 건너뛴다
        new = Monster.__new__(Monster)
        memo[id(self)] = new
        new.kind = self.kind
        new.hp = self.hp
        new.skills = list(self.skills)
        new.position = self.position                 # 튜플은 불변이라 공유해도 안전
        return new


class PrototypeRegistry:
    def __init__(self): self._protos: dict[str, Monster] = {}
    def register(self, name, proto): self._protos[name] = proto
    def create(self, name, **overrides):
        obj = copy.deepcopy(self._protos[name])
        for k, v in overrides.items():
            setattr(obj, k, v)
        return obj


if __name__ == "__main__":
    base = Document("template", ["draft"], {"font": "Nanum", "size": 11})

    shallow = base.clone(deep=False)
    shallow.title = "shallow"
    shallow.tags.append("shared?")
    print("얕은 복사 후 원본 tags:", base.tags)
    assert base.title == "template"                  # 재대입한 필드는 독립
    assert base.tags == ["draft", "shared?"]         # 리스트는 같은 객체를 공유

    deep = base.clone(deep=True)
    deep.tags.append("only-deep")
    deep.style["size"] = 20
    print("깊은 복사 후 원본 tags:", base.tags, "style:", base.style)
    assert "only-deep" not in base.tags and base.style["size"] == 11

    reg = PrototypeRegistry()
    Monster.load_count = 0
    t0 = time.perf_counter()
    reg.register("orc", Monster("orc", 100))
    reg.register("goblin", Monster("goblin", 40))
    made = [reg.create("orc", position=(i, i)) for i in range(50)]
    t1 = time.perf_counter()
    direct = [Monster("orc", 100) for _ in range(50)]
    t2 = time.perf_counter()
    print(f"프로토타입 2개 + 복제 50개: 무거운 초기화 2회, {(t1 - t0) * 1000:.0f}ms")
    print(f"직접 생성 50개: 무거운 초기화 50회, {(t2 - t1) * 1000:.0f}ms")
    assert Monster.load_count == 2 + 50
    made[0].skills.append("rage")
    assert made[1].skills == ["attack"]              # 복제본끼리 독립
    assert made[3].position == (3, 3)
    print("모든 검증 통과")
