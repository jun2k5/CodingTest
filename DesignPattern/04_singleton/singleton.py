"""싱글턴 패턴: 클래스의 인스턴스를 하나로 제한하고 전역 접근점을 준다.

python singleton.py 로 실행하면 스레드 경쟁 실험과 검증이 나온다.
"""
import threading
import time


# 1. __new__로 구현 (가장 흔한 형태, 스레드 안전하지 않음)
class NaiveSingleton:
    _instance = None
    created = 0

    def __new__(cls):
        if cls._instance is None:
            time.sleep(0.001)                   # 검사와 생성 사이에 다른 스레드가 끼어들 틈
            cls._instance = super().__new__(cls)
            NaiveSingleton.created += 1
        return cls._instance


# 2. 이중 검사 잠금 (double-checked locking)
class LockedSingleton:
    _instance = None
    _lock = threading.Lock()
    created = 0

    def __new__(cls):
        if cls._instance is None:               # 1차 검사: 이미 있으면 잠금 없이 반환
            with cls._lock:
                if cls._instance is None:       # 2차 검사: 잠금을 얻는 사이 다른 스레드가 만들었을 수 있다
                    time.sleep(0.001)
                    cls._instance = super().__new__(cls)
                    LockedSingleton.created += 1
        return cls._instance


# 3. 메타클래스: 여러 클래스에 재사용, __init__도 한 번만 실행
class SingletonMeta(type):
    _instances: dict = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Config(metaclass=SingletonMeta):
    def __init__(self, env="dev"):
        self.env = env
        self.values: dict = {}


class Registry(metaclass=SingletonMeta):
    def __init__(self):
        self.items: list = []


# 4. __new__ 방식의 함정: __init__은 매번 다시 실행된다
class Counter:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.count = 0                          # 두 번째 Counter() 호출 때 0으로 초기화된다


# 5. 테스트 친화적 대안: 인스턴스 하나를 만들어 주입한다
class Cache:
    def __init__(self): self.data = {}


class Service:
    def __init__(self, cache: Cache): self.cache = cache


def race(cls, n_threads=16):
    barrier = threading.Barrier(n_threads)
    ids = set()
    lock = threading.Lock()

    def worker():
        barrier.wait()                          # 모든 스레드가 동시에 출발
        obj = cls()
        with lock:
            ids.add(id(obj))

    ts = [threading.Thread(target=worker) for _ in range(n_threads)]
    for t in ts: t.start()
    for t in ts: t.join()
    return ids


if __name__ == "__main__":
    naive_ids = race(NaiveSingleton)
    locked_ids = race(LockedSingleton)
    print(f"NaiveSingleton : 스레드 16개 동시 생성 -> 생성 {NaiveSingleton.created}회, 서로 다른 객체 {len(naive_ids)}개")
    print(f"LockedSingleton: 스레드 16개 동시 생성 -> 생성 {LockedSingleton.created}회, 서로 다른 객체 {len(locked_ids)}개")
    assert NaiveSingleton.created > 1          # 경쟁 조건으로 여러 번 만들어진다
    assert LockedSingleton.created == 1 and len(locked_ids) == 1

    a, b = Config("prod"), Config("dev")
    assert a is b and a.env == "prod"          # 두 번째 인자는 무시된다
    assert Registry() is Registry() and Registry() is not a
    print(f"메타클래스: Config('prod') is Config('dev') = {a is b}, env = {b.env}")

    c1 = Counter()
    c1.count = 5
    c2 = Counter()
    assert c1 is c2 and c1.count == 0
    print(f"__new__ 함정: 같은 객체지만 count 5 -> {c1.count} (__init__ 재실행)")

    shared = Cache()
    s1, s2 = Service(shared), Service(shared)
    assert s1.cache is s2.cache
    s3 = Service(Cache())                      # 테스트에서는 새 캐시를 넣으면 된다
    assert s3.cache is not s1.cache
    print("주입 방식: 운영은 한 개 공유, 테스트는 매번 새 객체")
    print("모든 검증 통과")
