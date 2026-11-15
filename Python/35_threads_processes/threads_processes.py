"""35. 스레드와 프로세스: GIL, I/O vs CPU 작업, concurrent.futures, 경쟁 조건과 Lock, queue.Queue"""
import concurrent.futures as cf
import multiprocessing as mp
import queue
import sys
import threading
import time


def io_task(n):
    time.sleep(0.2)                  # 네트워크·디스크 대기를 흉내(대기 중에는 GIL을 놓는다)
    return n


def cpu_task(n):
    return sum(i * i for i in range(n))


def timed(label, fn):
    start = time.perf_counter()
    result = fn()
    print(f"{label}: {time.perf_counter() - start:.2f}s")
    return result


def io_bound():
    jobs = range(8)
    timed("I/O 8개 순차", lambda: [io_task(n) for n in jobs])
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        timed("I/O 8개 스레드", lambda: list(ex.map(io_task, jobs)))


def cpu_bound():
    jobs = [3_000_000] * 4
    seq = timed("CPU 4개 순차", lambda: [cpu_task(n) for n in jobs])
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        timed("CPU 4개 스레드(GIL 때문에 빨라지지 않음)", lambda: list(ex.map(cpu_task, jobs)))
    with cf.ProcessPoolExecutor(max_workers=4) as ex:
        res = timed("CPU 4개 프로세스", lambda: list(ex.map(cpu_task, jobs)))
    assert res == seq


def futures_api():
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        futures = {ex.submit(io_task, n): n for n in (3, 1, 2)}
        done_order = [futures[f] for f in cf.as_completed(futures)]
        print("as_completed(끝난 순서로):", sorted(done_order), "| 개수:", len(done_order))
        bad = ex.submit(lambda: 1 / 0)
        try:
            bad.result()
        except ZeroDivisionError:
            print("예외는 result()에서 다시 던져진다")


def race_condition():
    counter = {"n": 0}

    def unsafe(times):
        for _ in range(times):
            v = counter["n"]
            time.sleep(0)                # 읽기와 쓰기 사이에 다른 스레드로 전환되게 한다
            counter["n"] = v + 1

    threads = [threading.Thread(target=unsafe, args=(1000,)) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print("Lock 없음(기대 4000):", counter["n"])

    counter["n"] = 0
    lock = threading.Lock()

    def safe(times):
        for _ in range(times):
            with lock:
                v = counter["n"]
                time.sleep(0)
                counter["n"] = v + 1

    threads = [threading.Thread(target=safe, args=(1000,)) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print("Lock 사용:", counter["n"])
    assert counter["n"] == 4000


def producer_consumer():
    q = queue.Queue(maxsize=5)
    results = []

    def producer():
        for i in range(10):
            q.put(i)                     # 가득 차면 기다린다
        q.put(None)                      # 종료 신호

    def consumer():
        while (item := q.get()) is not None:
            results.append(item * 10)
            q.task_done()
        q.task_done()

    tp, tc = threading.Thread(target=producer), threading.Thread(target=consumer)
    tp.start(); tc.start(); tp.join(); tc.join()
    print("Queue 생산자·소비자:", results)
    assert results == [i * 10 for i in range(10)]


if __name__ == "__main__":           # Windows spawn 방식: 자식 프로세스가 이 파일을 다시 임포트한다
    print("시작 방식:", mp.get_start_method(), "| CPU 수:", mp.cpu_count() > 1)
    gil = sys._is_gil_enabled() if hasattr(sys, "_is_gil_enabled") else True
    print("GIL 활성:", gil)
    io_bound()
    cpu_bound()
    futures_api()
    race_condition()
    producer_consumer()
    print("모든 검증 통과")
