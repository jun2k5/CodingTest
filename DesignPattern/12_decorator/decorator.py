"""데코레이터 패턴: 객체를 감싸 같은 인터페이스를 유지한 채 기능을 덧붙인다.

python decorator.py 로 실행하면 검증과 예제 출력이 나온다.
"""
from abc import ABC, abstractmethod
import base64
import functools
import time
import zlib


class DataSource(ABC):                              # Component
    @abstractmethod
    def write(self, data: bytes) -> None: ...

    @abstractmethod
    def read(self) -> bytes: ...


class MemorySource(DataSource):                     # Concrete Component
    def __init__(self): self.stored = b""
    def write(self, data): self.stored = data
    def read(self): return self.stored


class SourceDecorator(DataSource):                  # Decorator: 감싼 객체에 위임
    def __init__(self, wrappee: DataSource): self.wrappee = wrappee
    def write(self, data): self.wrappee.write(data)
    def read(self): return self.wrappee.read()


class CompressionDecorator(SourceDecorator):
    def write(self, data): super().write(zlib.compress(data))
    def read(self): return zlib.decompress(super().read())


class Base64Decorator(SourceDecorator):             # 암호화 대신 인코딩으로 흉내
    def write(self, data): super().write(base64.b64encode(data))
    def read(self): return base64.b64decode(super().read())


class CountingDecorator(SourceDecorator):
    def __init__(self, wrappee):
        super().__init__(wrappee)
        self.writes = self.reads = 0
    def write(self, data):
        self.writes += 1
        super().write(data)
    def read(self):
        self.reads += 1
        return super().read()


# Python의 @데코레이터 문법: 함수를 감싸는 함수 (같은 아이디어, 대상이 함수)
def timed(fn):
    @functools.wraps(fn)                            # 이름·docstring 보존
    def wrapper(*args, **kwargs):
        t = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            wrapper.last_ms = (time.perf_counter() - t) * 1000
    wrapper.last_ms = None
    return wrapper


def retry(times):
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for i in range(times):
                try:
                    return fn(*args, **kwargs)
                except ConnectionError:
                    if i == times - 1:
                        raise
        return wrapper
    return deco


calls = {"n": 0}


@timed
@retry(3)
def flaky():
    """세 번째 호출에 성공한다."""
    calls["n"] += 1
    if calls["n"] < 3:
        raise ConnectionError
    return "ok"


if __name__ == "__main__":
    raw = MemorySource()
    data = ("design pattern " * 40).encode()
    src = Base64Decorator(CompressionDecorator(raw))   # 바깥부터: base64 -> 압축 -> 저장
    src.write(data)
    assert src.read() == data
    print(f"원본 {len(data)}B, 저장된 값 {len(raw.stored)}B (base64 인코딩 후 압축)")

    raw2 = MemorySource()
    src2 = CompressionDecorator(Base64Decorator(raw2))  # 순서를 바꾸면 저장 결과가 달라진다
    src2.write(data)
    assert src2.read() == data and raw.stored != raw2.stored
    print(f"순서를 바꾸면 저장된 값 {len(raw2.stored)}B (압축 후 base64 인코딩)")

    counter = CountingDecorator(src)
    counter.write(b"x")
    counter.read(); counter.read()
    assert (counter.writes, counter.reads) == (1, 2)
    print("감싼 개수와 상관없이 같은 인터페이스: writes=1 reads=2")

    assert flaky() == "ok" and calls["n"] == 3
    assert flaky.__name__ == "flaky" and flaky.last_ms is not None
    print(f"@timed @retry(3): 3번째 시도에 성공, __name__={flaky.__name__}")
    print("모든 검증 통과")
