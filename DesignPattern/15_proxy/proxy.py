"""프록시 패턴: 실제 객체 대신 대리 객체를 두어 접근을 제어한다.

python proxy.py 로 실행하면 가상·보호·캐시 프록시 검증이 나온다.
"""
from abc import ABC, abstractmethod
import time


class Image(ABC):                                    # Subject
    @abstractmethod
    def display(self) -> str: ...


class HighResImage(Image):                           # Real Subject
    loads = 0

    def __init__(self, path):
        HighResImage.loads += 1
        time.sleep(0.01)                             # 디스크에서 큰 파일 읽기 흉내
        self.path = path

    def display(self): return f"display {self.path}"


# 1. 가상 프록시: 실제로 필요할 때까지 생성을 미룬다 (지연 로딩)
class LazyImage(Image):
    def __init__(self, path):
        self.path = path
        self._real = None

    def display(self):
        if self._real is None:
            self._real = HighResImage(self.path)
        return self._real.display()


# 2. 보호 프록시: 권한 검사
class Document:
    def __init__(self): self.text = "v1"
    def read(self): return self.text
    def write(self, t): self.text = t


class DocumentProxy:
    def __init__(self, doc: Document, role: str):
        self._doc, self._role = doc, role

    def read(self): return self._doc.read()

    def write(self, t):
        if self._role != "editor":
            raise PermissionError(f"{self._role}는 수정 불가")
        self._doc.write(t)


# 3. 캐시 프록시: 같은 요청 결과를 저장해 둔다
class WeatherAPI:
    calls = 0
    def get(self, city):
        WeatherAPI.calls += 1
        return {"seoul": 21, "busan": 24}.get(city)


class CachedWeather:
    def __init__(self, api, ttl=60.0, clock=time.monotonic):
        self.api, self.ttl, self.clock = api, ttl, clock
        self._cache: dict = {}

    def get(self, city):
        hit = self._cache.get(city)
        now = self.clock()
        if hit and now - hit[1] < self.ttl:
            return hit[0]
        value = self.api.get(city)
        self._cache[city] = (value, now)
        return value


# 4. 범용 프록시: __getattr__로 모든 호출을 가로채 기록한다
class LoggingProxy:
    def __init__(self, target):
        object.__setattr__(self, "_target", target)
        object.__setattr__(self, "log", [])

    def __getattr__(self, name):                     # 프록시에 없는 속성만 여기로 온다
        attr = getattr(self._target, name)
        if callable(attr):
            def wrapped(*a, **kw):
                self.log.append(name)
                return attr(*a, **kw)
            return wrapped
        return attr


if __name__ == "__main__":
    gallery = [LazyImage(f"photo{i}.png") for i in range(100)]
    assert HighResImage.loads == 0
    print(gallery[3].display(), gallery[3].display())
    print(f"가상 프록시: 이미지 100개 중 실제 로딩 {HighResImage.loads}회")
    assert HighResImage.loads == 1

    doc = Document()
    viewer, editor = DocumentProxy(doc, "viewer"), DocumentProxy(doc, "editor")
    editor.write("v2")
    assert viewer.read() == "v2"
    try:
        viewer.write("hack")
        raise AssertionError
    except PermissionError as e:
        print("보호 프록시:", e)

    now = [0.0]
    w = CachedWeather(WeatherAPI(), ttl=60, clock=lambda: now[0])
    for t in [0, 10, 59, 61, 70]:
        now[0] = t
        w.get("seoul")
    print(f"캐시 프록시: 5번 조회, 실제 API 호출 {WeatherAPI.calls}회 (TTL 60초)")
    assert WeatherAPI.calls == 2

    p = LoggingProxy([3, 1, 2])
    p.append(0); p.sort()
    assert p._target == [0, 1, 2, 3] and p.log == ["append", "sort"]
    print("로깅 프록시:", p.log)
    print("모든 검증 통과")
