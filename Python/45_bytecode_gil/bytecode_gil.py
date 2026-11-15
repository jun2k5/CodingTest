"""45. 바이트코드와 GIL: 컴파일 → 코드 객체 → 바이트코드, dis, 적응형 특수화, GIL과 스레드, free-threading"""
import dis
import io
import sys
import threading
import time


def add(a, b):
    c = a + b
    return c


def code_object():
    co = add.__code__
    print("코드 객체:", co.co_name, "| 인자 수:", co.co_argcount, "| 지역 변수:", co.co_varnames)
    print("원본 바이트코드는 bytes:", type(co.co_code).__name__)
    src = "x = 1 + 2"
    compiled = compile(src, "<demo>", "exec")
    folded = [(i.opname, i.argval) for i in dis.get_instructions(compiled) if i.opname.startswith(("LOAD_SMALL", "LOAD_CONST", "BINARY"))]
    print("상수 접기(1 + 2 → 3):", folded)
    assert ("LOAD_SMALL_INT", 3) in folded and not any(op == "BINARY_OP" for op, _ in folded)


def disassemble():
    ops = [ins.opname for ins in dis.get_instructions(add)]
    print("add의 명령어:", ops)
    assert "BINARY_OP" in ops and "RETURN_VALUE" in ops

    def loop_global():
        total = 0
        for i in range(10):
            total += len("ab")       # len은 전역(내장) 조회
        return total

    def loop_local(len=len):
        total = 0
        for i in range(10):
            total += len("ab")       # 지역 변수 조회
        return total

    def len_loads(f):
        return sorted({ins.opname for ins in dis.get_instructions(f) if "len" in ins.argrepr})
    print("전역 len 조회:", len_loads(loop_global), "| 지역 len 조회:", len_loads(loop_local))
    assert len_loads(loop_global) == ["LOAD_GLOBAL"] and "LOAD_GLOBAL" not in len_loads(loop_local)


def specialization():
    def hot(n):
        s = 0
        for i in range(n):
            s = s + i
        return s

    for _ in range(100):           # 여러 번 실행해 "뜨거운" 코드로 만든다
        hot(100)
    adaptive = {ins.opname for ins in dis.get_instructions(hot, adaptive=True)}
    special = sorted(op for op in adaptive if op.startswith("BINARY_OP_") or op.startswith("FOR_ITER_"))
    print("특수화된 명령 예:", special)
    assert any(op.startswith("BINARY_OP_ADD_INT") for op in adaptive)


def gil_and_threads():
    print("GIL 활성화:", sys._is_gil_enabled())

    def count(n):
        while n > 0:
            n -= 1

    N = 5_000_000
    t0 = time.perf_counter()
    count(N); count(N)
    serial = time.perf_counter() - t0

    t0 = time.perf_counter()
    ts = [threading.Thread(target=count, args=(N,)) for _ in range(2)]
    for t in ts: t.start()
    for t in ts: t.join()
    threaded = time.perf_counter() - t0
    print(f"순차 {serial:.2f}s | 스레드 2개 {threaded:.2f}s")   # 실행마다 다름
    if sys._is_gil_enabled():
        assert threaded > serial * 0.7      # GIL: CPU 작업은 스레드로 나눠도 빨라지지 않는다

    counter = 0
    lock = threading.Lock()

    def unsafe():
        nonlocal counter
        for _ in range(100_000):
            with lock:               # += 는 여러 바이트코드라 GIL이 있어도 원자적이지 않다
                counter += 1
    ts = [threading.Thread(target=unsafe) for _ in range(4)]
    for t in ts: t.start()
    for t in ts: t.join()
    print("락으로 보호한 카운터:", counter)
    assert counter == 400_000

    ops = [ins.opname for ins in dis.get_instructions("counter += 1")]
    print("counter += 1 의 명령:", [op for op in ops if op not in ("RESUME", "RETURN_VALUE", "LOAD_CONST")])
    print("스레드 전환 간격(초):", sys.getswitchinterval())


if __name__ == "__main__":
    code_object()
    disassemble()
    specialization()
    gil_and_threads()
    print("모든 검증 통과")
