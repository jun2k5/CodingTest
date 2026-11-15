"""06. list·dict·set 내부와 시간복잡도: 동적 배열, 해시 테이블, 순서 보장"""
import sys
import timeit


def list_overallocation():
    lst, sizes = [], []
    last = sys.getsizeof(lst)
    for i in range(20):
        lst.append(i)
        size = sys.getsizeof(lst)
        if size != last:
            sizes.append((len(lst), size))
            last = size
    print("크기가 바뀐 시점 (원소 수, 바이트):", sizes)
    assert len(sizes) < 20          # 매번이 아니라 가끔만 다시 할당한다


def list_costs():
    n = 20_000
    t_end = timeit.timeit("lst.append(0); lst.pop()", setup=f"lst=list(range({n}))", number=20_000)
    t_front = timeit.timeit("lst.insert(0, 0); lst.pop(0)", setup=f"lst=list(range({n}))", number=20_000)
    print(f"끝에서 append/pop: {t_end * 1000:.1f}ms, 앞에서 insert/pop(0): {t_front * 1000:.1f}ms")
    assert t_front > t_end


def membership():
    data = list(range(100_000))
    as_set = set(data)
    t_list = timeit.timeit(lambda: 99_999 in data, number=200)
    t_set = timeit.timeit(lambda: 99_999 in as_set, number=200)
    print(f"in 검사 200회 - list: {t_list * 1000:.2f}ms, set: {t_set * 1000:.3f}ms")
    assert t_list > t_set


def dict_order_and_hash():
    d = {}
    for k in ["banana", "apple", "cherry"]:
        d[k] = len(k)
    del d["apple"]
    d["apple"] = 5
    print("삽입 순서 유지:", list(d))
    assert list(d) == ["banana", "cherry", "apple"]

    print("hash(1) == hash(1.0) == hash(True):", hash(1) == hash(1.0) == hash(True))
    mixed = {1: "int", 1.0: "float", True: "bool"}
    print("같은 키로 취급:", mixed)
    assert mixed == {1: "bool"}

    try:
        {[1, 2]: "list"}
    except TypeError as e:
        print("가변 객체는 키가 될 수 없다:", e)


class BadHash:
    def __init__(self, v):
        self.v = v

    def __hash__(self):
        return 42                    # 모든 객체가 같은 해시 → 충돌

    def __eq__(self, other):
        return isinstance(other, BadHash) and self.v == other.v


class GoodHash(BadHash):
    def __hash__(self):
        return hash(self.v)


def collision_cost():
    def build(cls):
        return {cls(i) for i in range(2000)}
    t_bad = timeit.timeit(lambda: build(BadHash), number=3)
    t_good = timeit.timeit(lambda: build(GoodHash), number=3)
    print(f"해시 충돌 시 set 생성: {t_bad * 1000:.0f}ms, 정상 해시: {t_good * 1000:.1f}ms")
    assert t_bad > t_good * 10


def set_operations():
    a, b = {1, 2, 3, 4}, {3, 4, 5}
    print("합", a | b, "교", a & b, "차", a - b, "대칭차", a ^ b)
    assert a & b == {3, 4}
    frozen = frozenset({1, 2})
    print("frozenset은 키가 될 수 있다:", {frozen: "ok"}[frozenset({2, 1})])


if __name__ == "__main__":
    list_overallocation()
    list_costs()
    membership()
    dict_order_and_hash()
    collision_cost()
    set_operations()
    print("모든 검증 통과")
