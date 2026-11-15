"""11. defaultdict: __missing__, default_factory, 중첩 구조, setdefault·get과 비교"""
from collections import defaultdict

WORDS = ["apple", "avocado", "banana", "blueberry", "cherry", "apple"]


def grouping_three_ways():
    # 1) 기초: 키가 있는지 직접 확인
    g1 = {}
    for w in WORDS:
        if w[0] not in g1:
            g1[w[0]] = []
        g1[w[0]].append(w)

    # 2) setdefault: 키가 없으면 기본값을 넣고 그 값을 반환
    g2 = {}
    for w in WORDS:
        g2.setdefault(w[0], []).append(w)

    # 3) defaultdict: 없는 키를 읽는 순간 default_factory()로 만들어 넣는다
    g3 = defaultdict(list)
    for w in WORDS:
        g3[w[0]].append(w)

    print("defaultdict:", dict(g3))
    assert g1 == g2 == g3


def factories():
    counts = defaultdict(int)          # int() == 0
    for w in WORDS:
        counts[w] += 1
    print("int 팩토리 카운트:", dict(counts))

    unique = defaultdict(set)
    for w in WORDS:
        unique[len(w)].add(w)
    print("set 팩토리:", {k: sorted(v) for k, v in sorted(unique.items())})

    labeled = defaultdict(lambda: "미분류")
    labeled["apple"] = "과일"
    print("람다 팩토리:", labeled["apple"], labeled["rock"])


def missing_semantics():
    d = defaultdict(list)
    print("get은 만들지 않는다:", d.get("x"), "| in 검사:", "x" in d, "| 길이:", len(d))
    _ = d["x"]                          # 읽기만 해도 키가 생긴다
    print("[] 접근 후:", dict(d), "| 길이:", len(d))
    assert "x" in d

    plain = defaultdict()               # default_factory=None이면 일반 dict처럼 KeyError
    try:
        plain["y"]
    except KeyError:
        print("팩토리 None → KeyError")


class LowerKeyDict(dict):
    """__missing__은 dict 하위 클래스라면 누구나 구현할 수 있다"""

    def __missing__(self, key):
        if isinstance(key, str) and key.lower() in self:
            return self[key.lower()]
        raise KeyError(key)


def custom_missing():
    d = LowerKeyDict(name="kim")
    print("__missing__ 직접 구현:", d["NAME"], "| get은 __missing__을 안 부른다:", d.get("NAME"))
    assert d["NAME"] == "kim" and d.get("NAME") is None


def nested():
    def tree():
        return defaultdict(tree)        # 자기 자신을 팩토리로: 임의 깊이

    t = tree()
    t["user"]["profile"]["name"] = "kim"
    t["user"]["settings"]["theme"] = "dark"

    def to_dict(x):
        return {k: to_dict(v) for k, v in x.items()} if isinstance(x, dict) else x
    print("자동 중첩:", to_dict(t))

    sales = defaultdict(lambda: defaultdict(int))
    for region, item, qty in [("서울", "A", 3), ("서울", "B", 1), ("부산", "A", 2), ("서울", "A", 4)]:
        sales[region][item] += qty
    print("2단 집계:", {r: dict(v) for r, v in sales.items()})
    assert sales["서울"]["A"] == 7


def graph_adjacency():
    edges = [("a", "b"), ("a", "c"), ("b", "c"), ("c", "a")]
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
    print("인접 리스트:", dict(graph), "| 없는 정점:", graph["z"])


if __name__ == "__main__":
    grouping_three_ways()
    factories()
    missing_semantics()
    custom_missing()
    nested()
    graph_adjacency()
    print("모든 검증 통과")
