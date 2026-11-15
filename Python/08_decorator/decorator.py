"""08. 데코레이터 원리: 함수 객체, 감싸기, 인자 있는 데코레이터, 쌓기, 클래스 데코레이터"""
import functools
import time


def functions_are_objects():
    def greet(name):
        return f"hi {name}"

    alias = greet
    handlers = {"greet": greet}
    print("함수도 객체:", alias("kim"), handlers["greet"]("lee"), greet.__name__)


def log_calls(func):
    @functools.wraps(func)          # 이름, docstring, __wrapped__ 등을 원본에서 복사
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        wrapper.calls.append(f"{func.__name__}{args} -> {result}")
        return result
    wrapper.calls = []
    return wrapper


@log_calls
def add(a, b):
    """두 수를 더한다"""
    return a + b


def without_wraps(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


@without_wraps
def documented():
    """설명이 있는 함수"""


def retry(times, exceptions=(Exception,)):
    """인자를 받는 데코레이터: 데코레이터를 만드는 함수"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt == times:
                        raise
        return wrapper
    return decorator


attempts = []


@retry(times=3, exceptions=(ValueError,))
def flaky():
    attempts.append(1)
    if len(attempts) < 3:
        raise ValueError("일시 오류")
    return "성공"


def tag(name):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return f"<{name}>{func(*args, **kwargs)}</{name}>"
        return wrapper
    return decorator


@tag("b")
@tag("i")
def text():
    return "hello"


def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            wrapper.last_elapsed = time.perf_counter() - start
    return wrapper


@timer
def slow():
    time.sleep(0.01)
    return "done"


REGISTRY = {}


def register(cls):
    """클래스 데코레이터: 클래스를 받아 (보통 같은) 클래스를 돌려준다"""
    REGISTRY[cls.__name__.lower()] = cls
    return cls


@register
class JsonExporter:
    pass


@register
class CsvExporter:
    pass


class CountCalls:
    """클래스로 만든 데코레이터: __call__로 호출 가능한 객체"""

    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func, self.count = func, 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        return self.func(*args, **kwargs)


@CountCalls
def ping():
    return "pong"


if __name__ == "__main__":
    functions_are_objects()

    print("add:", add(2, 3), add(4, 5), "| 기록:", add.calls)
    print("wraps 있음:", add.__name__, add.__doc__, "| 원본:", add.__wrapped__(1, 1))
    print("wraps 없음:", documented.__name__, documented.__doc__)
    assert add.__name__ == "add" and documented.__name__ == "wrapper"

    print("retry:", flaky(), "| 시도 횟수:", len(attempts))
    assert len(attempts) == 3

    print("쌓기 순서:", text())
    assert text() == "<b><i>hello</i></b>"

    print("timer:", slow(), "| 10ms 이상:", slow.last_elapsed >= 0.01)

    print("등록된 클래스:", sorted(REGISTRY))
    assert REGISTRY["jsonexporter"] is JsonExporter

    ping(); ping()
    print("클래스 데코레이터 객체:", ping.count, ping.__name__)
    assert ping.count == 2
    print("모든 검증 통과")
