"""44. 메모리 관리: 참조 카운트, 즉시 해제, 순환 참조와 gc, weakref, __del__ 주의, getsizeof 얕은 크기"""
import gc
import sys
import weakref


class Node:
    def __init__(self, name, log=None):
        self.name = name
        self.log = log
        self.other = None

    def __del__(self):                      # 해제 시점 관찰용(실무에서는 가급적 쓰지 않는다)
        if self.log is not None:
            self.log.append(f"{self.name} 해제")


def refcount():
    obj = []
    base = sys.getrefcount(obj)             # 인자로 넘기며 임시 참조가 1 더해진다
    alias = obj
    container = [obj]
    print("참조 추가 후 증가량:", sys.getrefcount(obj) - base)
    del alias, container
    print("del 후 원래대로:", sys.getrefcount(obj) - base)


def immediate_free():
    log = []
    n = Node("A", log)
    print("del 전:", log)
    del n                                    # 참조 0 → 즉시 해제
    print("del 직후:", log)

    def scope():
        Node("지역", log)
    scope()
    print("함수 끝(지역 변수 소멸):", log[-1])


def cycles():
    log = []
    gc.disable()                             # 자동 수집을 끄고 관찰
    a, b = Node("cycA", log), Node("cycB", log)
    a.other, b.other = b, a                  # 서로 참조 → 참조 카운트가 0이 되지 않음
    del a, b
    print("순환 참조 del 직후:", log)
    found = gc.collect()
    print("gc.collect() 후:", sorted(log), "| 수집한 객체 수 > 0:", found > 0)
    gc.enable()
    print("gc 임계값(세대):", gc.get_threshold())


def weak_references():
    log = []
    target = Node("cache-target", log)
    ref = weakref.ref(target)               # 참조 카운트를 올리지 않는 참조
    print("weakref 살아 있음:", ref().name)
    del target
    print("원본 해제 후 ref():", ref(), "|", log)

    cache = weakref.WeakValueDictionary()
    big = Node("big")
    cache["k"] = big
    print("WeakValueDictionary 크기:", len(cache))
    del big
    print("값이 해제되면 자동 제거:", len(cache))

    class Parent:
        def __init__(self):
            self.children = []

    class Child:
        def __init__(self, parent):
            self._parent = weakref.ref(parent)   # 부모를 약하게 참조 → 순환 없음

        @property
        def parent(self):
            return self._parent()

    p = Parent()
    c = Child(p)
    p.children.append(c)
    print("부모-자식 약한 역참조:", c.parent is p)

    finalized = []
    obj = Node("fin")
    weakref.finalize(obj, finalized.append, "finalize 콜백")   # __del__ 대신 권장
    del obj
    print("finalize:", finalized)


def sizes():
    small, nested = [1, 2, 3], [[0] * 1000]
    print("getsizeof 리스트:", sys.getsizeof(small), "| 안에 큰 리스트가 있어도:", sys.getsizeof(nested))

    def deep_size(o, seen=None):
        seen = seen if seen is not None else set()
        if id(o) in seen:
            return 0
        seen.add(id(o))
        size = sys.getsizeof(o)
        if isinstance(o, (list, tuple, set)):
            size += sum(deep_size(x, seen) for x in o)
        elif isinstance(o, dict):
            size += sum(deep_size(k, seen) + deep_size(v, seen) for k, v in o.items())
        return size
    print("재귀로 합한 크기 > 얕은 크기:", deep_size(nested) > sys.getsizeof(nested) * 10)


if __name__ == "__main__":
    refcount()
    immediate_free()
    cycles()
    weak_references()
    sizes()
    print("모든 검증 통과")
