"""플라이웨이트 패턴: 공유 가능한 상태(내재 상태)를 객체 하나로 모아 여러 곳에서 함께 쓴다.

python flyweight.py 로 실행하면 메모리 사용량 비교와 검증이 나온다.
"""
import random
import sys
import tracemalloc


# 공유하지 않는 버전: 나무마다 텍스처·메시 데이터를 따로 가진다
class TreeHeavy:
    def __init__(self, x, y, species, color, texture):
        self.x, self.y = x, y                       # 외재 상태 (나무마다 다름)
        self.species, self.color = species, color   # 내재 상태 (종류마다 같음)
        self.texture = texture


# 플라이웨이트: 내재 상태만 가진다. 불변이어야 공유가 안전하다
class TreeType:
    __slots__ = ("species", "color", "texture")

    def __init__(self, species, color, texture):
        self.species, self.color, self.texture = species, color, texture

    def draw(self, x, y):                           # 외재 상태는 인자로 받는다
        return f"{self.species}({self.color}) at ({x},{y})"


class TreeTypeFactory:
    _cache: dict = {}

    @classmethod
    def get(cls, species, color):
        key = (species, color)
        if key not in cls._cache:
            cls._cache[key] = TreeType(species, color, bytes(10_000))   # 텍스처 10KB 흉내
        return cls._cache[key]


class Tree:
    __slots__ = ("x", "y", "type")

    def __init__(self, x, y, tree_type: TreeType):
        self.x, self.y, self.type = x, y, tree_type

    def draw(self): return self.type.draw(self.x, self.y)


KINDS = [("oak", "green"), ("pine", "dark"), ("birch", "white"), ("maple", "red")]


def measure(fn):
    tracemalloc.start()
    obj = fn()
    cur, _ = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return obj, cur


if __name__ == "__main__":
    N = 10_000
    rng = random.Random(0)
    spots = [(rng.randint(0, 999), rng.randint(0, 999), *rng.choice(KINDS)) for _ in range(N)]

    heavy, mem_heavy = measure(lambda: [TreeHeavy(x, y, s, c, bytes(10_000)) for x, y, s, c in spots])
    light, mem_light = measure(lambda: [Tree(x, y, TreeTypeFactory.get(s, c)) for x, y, s, c in spots])

    print(f"나무 {N}그루, 종류 {len(KINDS)}개")
    print(f"공유 안 함: {mem_heavy / 1024 / 1024:.1f} MB")
    print(f"플라이웨이트: {mem_light / 1024 / 1024:.2f} MB (TreeType 객체 {len(TreeTypeFactory._cache)}개)")
    assert len(TreeTypeFactory._cache) == len(KINDS)
    assert mem_light * 50 < mem_heavy
    for h, l in zip(heavy, light):
        assert (h.x, h.y, h.species, h.color) == (l.x, l.y, l.type.species, l.type.color)
    print(light[0].draw())

    # 언어 차원의 플라이웨이트: CPython 작은 정수 캐시, 문자열 인터닝
    a, b = int("256"), int("256")
    c, d = int("257"), int("257")
    print(f"CPython: int 256 공유 = {a is b}, int 257 공유 = {c is d}")
    s1 = sys.intern("".join(["fly", "weight"]))
    s2 = sys.intern("".join(["fly", "weight"]))
    assert s1 is s2
    print("sys.intern으로 같은 문자열 객체 공유 =", s1 is s2)
    print("모든 검증 통과")
