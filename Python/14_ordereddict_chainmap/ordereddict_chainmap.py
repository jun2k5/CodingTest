"""14. OrderedDict와 ChainMap: dict와 다른 점, move_to_end, LRU 캐시, 설정 계층"""
import argparse
from collections import ChainMap, OrderedDict


def ordered_vs_dict():
    a = {"x": 1, "y": 2}
    b = {"y": 2, "x": 1}
    oa, ob = OrderedDict(a), OrderedDict(b)
    print("dict ==:", a == b, "| OrderedDict ==:", oa == ob, "| 섞어서:", oa == b)
    assert a == b and oa != ob and oa == b   # 순서 비교는 OrderedDict끼리만

    od = OrderedDict.fromkeys("abcde")
    od.move_to_end("b")                 # 맨 뒤로
    od.move_to_end("d", last=False)     # 맨 앞으로
    print("move_to_end:", "".join(od))
    print("popitem(last=False):", od.popitem(last=False)[0], "| 남은:", "".join(od))
    assert "".join(od) == "aceb"


class LRUCache:
    """최근에 쓴 것을 뒤로 보내고, 넘치면 맨 앞(가장 오래 안 쓴 것)을 버린다"""

    def __init__(self, capacity):
        self.capacity = capacity
        self.data = OrderedDict()

    def get(self, key):
        if key not in self.data:
            return None
        self.data.move_to_end(key)
        return self.data[key]

    def put(self, key, value):
        self.data[key] = value
        self.data.move_to_end(key)
        if len(self.data) > self.capacity:
            self.data.popitem(last=False)


def lru_demo():
    cache = LRUCache(2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.get("a")          # a를 최근 사용으로
    cache.put("c", 3)       # 넘침 → 가장 오래 안 쓴 b를 버림
    print("LRU 남은 키:", list(cache.data), "| b:", cache.get("b"))
    assert list(cache.data) == ["a", "c"]


def chainmap_layers():
    defaults = {"host": "localhost", "port": 8000, "debug": False}
    env = {"port": "9000"}
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", default=None)
    cli = {k: v for k, v in vars(parser.parse_args(["--debug"])).items() if v is not None}

    config = ChainMap(cli, env, defaults)     # 앞쪽이 우선
    print("설정 조회:", config["host"], config["port"], config["debug"])
    assert (config["port"], config["debug"]) == ("9000", True)
    print("병합된 보기:", dict(config))

    config["host"] = "0.0.0.0"                # 쓰기는 항상 첫 번째 매핑에
    print("쓰기 후 cli:", cli, "| defaults host:", defaults["host"])
    assert cli["host"] == "0.0.0.0" and defaults["host"] == "localhost"


def chainmap_scopes():
    globals_ = ChainMap({"x": "global"})
    local = globals_.new_child({"x": "local", "y": 1})
    print("새 자식 스코프:", local["x"], "| 부모:", local.parents["x"], "| maps 수:", len(local.maps))
    assert local["x"] == "local" and local.parents["x"] == "global"


if __name__ == "__main__":
    ordered_vs_dict()
    lru_demo()
    chainmap_layers()
    chainmap_scopes()
    print("모든 검증 통과")
