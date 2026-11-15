"""24. contextlib: with 프로토콜, contextmanager, suppress, ExitStack, closing, redirect_stdout, chdir, nullcontext"""
import contextlib
import io
import os
import tempfile
import time


class Timer:
    """클래스로 만든 컨텍스트 매니저: __enter__ / __exit__"""

    def __enter__(self):
        self.start = time.perf_counter()
        return self                        # as 뒤의 이름에 묶이는 값

    def __exit__(self, exc_type, exc, tb):
        self.elapsed = time.perf_counter() - self.start
        self.error = exc_type.__name__ if exc_type else None
        return False                       # True면 예외를 삼킨다


def protocol():
    with Timer() as t:
        sum(range(10_000))
    print("Timer: 측정됨", t.elapsed > 0, "| 예외:", t.error)
    try:
        with Timer() as t2:
            1 / 0
    except ZeroDivisionError:
        print("__exit__이 예외 정보를 받음:", t2.error)


@contextlib.contextmanager
def tag(name, log):
    log.append(f"<{name}>")                # yield 앞 = __enter__
    try:
        yield name.upper()                 # yield 값 = as에 묶이는 값
    finally:
        log.append(f"</{name}>")           # yield 뒤 = __exit__ (finally로 예외 시에도)


def generator_based():
    log = []
    with tag("div", log) as v:
        log.append(f"본문 {v}")
    print("contextmanager:", log)
    log.clear()
    try:
        with tag("p", log):
            raise ValueError("중간 오류")
    except ValueError:
        pass
    print("예외가 나도 정리:", log)
    assert log == ["<p>", "</p>"]


@contextlib.contextmanager
def transaction(db):
    snapshot = dict(db)
    try:
        yield db
    except Exception:
        db.clear()
        db.update(snapshot)                # 롤백
        raise


def rollback_demo():
    db = {"balance": 100}
    try:
        with transaction(db) as d:
            d["balance"] -= 30
            raise RuntimeError("결제 실패")
    except RuntimeError:
        pass
    print("롤백 후:", db)
    assert db == {"balance": 100}


def suppress_demo():
    with contextlib.suppress(FileNotFoundError):
        os.remove("존재하지_않는_파일.txt")
    print("suppress: FileNotFoundError 무시하고 계속")


def exitstack_demo():
    tmpdir = tempfile.mkdtemp()
    paths = [os.path.join(tmpdir, f"f{i}.txt") for i in range(3)]
    with contextlib.ExitStack() as stack:
        files = [stack.enter_context(open(p, "w", encoding="utf-8")) for p in paths]
        for i, f in enumerate(files):
            f.write(f"line {i}")
        stack.callback(lambda: print("  ExitStack 콜백 실행(마지막에 등록 → 먼저 실행)"))
        print("열린 파일 수:", sum(not f.closed for f in files))
    print("with 종료 후 모두 닫힘:", all(f.closed for f in files))


def misc_tools():
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        print("화면 대신 버퍼로")
    print("redirect_stdout 캡처:", buf.getvalue().strip())

    before = os.getcwd()
    with contextlib.chdir(tempfile.gettempdir()):          # 3.11+
        inside = os.getcwd()
    print("chdir 복원:", os.getcwd() == before, inside != before)

    def process(use_lock, lock):
        with lock if use_lock else contextlib.nullcontext():
            return "처리"
    print("nullcontext:", process(False, None))

    class Resource:
        def close(self):
            print("  closing()이 close() 호출")
    with contextlib.closing(Resource()):
        pass


if __name__ == "__main__":
    protocol()
    generator_based()
    rollback_demo()
    suppress_demo()
    exitstack_demo()
    misc_tools()
    print("모든 검증 통과")
