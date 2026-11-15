"""07. 이터레이터와 제너레이터: 프로토콜, yield, yield from, send, 지연 평가"""


class Countdown:
    """이터러블: __iter__가 매번 새 이터레이터를 돌려준다"""

    def __init__(self, start):
        self.start = start

    def __iter__(self):
        return CountdownIterator(self.start)


class CountdownIterator:
    """이터레이터: __next__로 값을 내고, 끝나면 StopIteration"""

    def __init__(self, current):
        self.current = current

    def __iter__(self):
        return self

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        self.current -= 1
        return self.current + 1


def countdown_gen(start):
    """같은 동작을 제너레이터 함수로: 상태 저장과 StopIteration을 파이썬이 처리"""
    while start > 0:
        yield start
        start -= 1


def protocol():
    it = iter([10, 20])
    print("next:", next(it), next(it), "| 기본값:", next(it, "끝"))

    cd = Countdown(3)
    print("이터러블은 여러 번 순회:", list(cd), list(cd))
    assert list(cd) == [3, 2, 1] == list(cd)

    gen = countdown_gen(3)
    print("제너레이터는 한 번:", list(gen), list(gen))
    print("for 문이 하는 일 = iter() 후 next() 반복, StopIteration에서 종료")


def laziness():
    log = []

    def numbers():
        for i in range(5):
            log.append(f"생성 {i}")
            yield i

    gen = numbers()
    print("만들기만 했을 때 log:", log)
    first_two = [next(gen), next(gen)]
    print("두 개 꺼낸 뒤 log:", log, first_two)
    assert log == ["생성 0", "생성 1"]


def pipeline():
    lines = ["10", "x", "25", "", "7"]
    cleaned = (s.strip() for s in lines)
    numbers = (int(s) for s in cleaned if s.isdigit())
    big = (n for n in numbers if n > 8)
    print("파이프라인 결과:", list(big))


def yield_from():
    def inner():
        yield 1
        yield 2
        return "inner 완료"        # return 값은 StopIteration.value로 전달

    def outer():
        result = yield from inner()  # 하위 제너레이터에 위임하고 반환값을 받는다
        yield result

    print("yield from:", list(outer()))
    assert list(outer()) == [1, 2, "inner 완료"]

    def flatten(items):
        for x in items:
            if isinstance(x, list):
                yield from flatten(x)
            else:
                yield x
    print("재귀 평탄화:", list(flatten([1, [2, [3, 4]], 5])))


def send_coroutine():
    def running_average():
        total, count, avg = 0.0, 0, None
        while True:
            value = yield avg       # 값을 내보내고, send()로 들어온 값을 받는다
            total += value
            count += 1
            avg = total / count

    ra = running_average()
    next(ra)                         # 첫 yield까지 진행(프라이밍)
    results = [ra.send(v) for v in (10, 20, 60)]
    print("send로 이동 평균:", results)
    assert results == [10.0, 15.0, 30.0]


def generator_state_and_close():
    import inspect

    def g():
        try:
            yield 1
            yield 2
        finally:
            print("  finally 실행(close 또는 소멸 시)")

    gen = g()
    print("상태:", inspect.getgeneratorstate(gen))
    next(gen)
    print("상태:", inspect.getgeneratorstate(gen))
    gen.close()
    print("상태:", inspect.getgeneratorstate(gen))


if __name__ == "__main__":
    protocol()
    laziness()
    pipeline()
    yield_from()
    send_coroutine()
    generator_state_and_close()
    print("모든 검증 통과")
