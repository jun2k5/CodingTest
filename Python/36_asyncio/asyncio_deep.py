"""36. asyncio: 코루틴과 이벤트 루프, gather, TaskGroup, timeout, Semaphore, 블로킹 함정과 to_thread, async with/for"""
import asyncio
import contextlib
import time


async def fetch(name, delay):
    await asyncio.sleep(delay)            # await 지점에서 이벤트 루프에 제어를 넘긴다
    return f"{name}({delay}s)"


async def coroutine_basics():
    coro = fetch("a", 0.1)
    print("코루틴 함수 호출 결과:", type(coro).__name__, "| 아직 실행 안 됨")
    print("await 결과:", await coro)


async def sequential_vs_concurrent():
    start = time.perf_counter()
    for n in ("a", "b", "c"):
        await fetch(n, 0.2)
    seq = time.perf_counter() - start

    start = time.perf_counter()
    results = await asyncio.gather(fetch("a", 0.2), fetch("b", 0.2), fetch("c", 0.2))
    conc = time.perf_counter() - start
    print(f"순차 await: {seq:.2f}s | gather: {conc:.2f}s | 결과 순서는 인자 순서: {results}")


async def task_group():
    async with asyncio.TaskGroup() as tg:                     # 3.11+
        t1 = tg.create_task(fetch("x", 0.1))
        t2 = tg.create_task(fetch("y", 0.05))
    print("TaskGroup 결과:", t1.result(), t2.result())

    async def fail():
        await asyncio.sleep(0.05)
        raise ValueError("작업 실패")

    cancelled = []

    async def slow():
        try:
            await asyncio.sleep(1)
        except asyncio.CancelledError:
            cancelled.append("slow 취소됨")
            raise

    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(fail())
            tg.create_task(slow())
    except* ValueError as eg:
        print("TaskGroup 예외(ExceptionGroup):", [str(e) for e in eg.exceptions], "| 나머지:", cancelled)


async def timeouts():
    try:
        async with asyncio.timeout(0.1):                       # 3.11+
            await fetch("느린 API", 1)
    except TimeoutError:
        print("timeout: 0.1초 안에 안 끝나 취소")
    print("wait_for:", await asyncio.wait_for(fetch("빠름", 0.01), timeout=1))


async def limit_concurrency():
    sem = asyncio.Semaphore(2)
    running, peak = 0, 0

    async def limited(i):
        nonlocal running, peak
        async with sem:
            running += 1
            peak = max(peak, running)
            await asyncio.sleep(0.05)
            running -= 1
            return i

    results = await asyncio.gather(*(limited(i) for i in range(6)))
    print("Semaphore(2): 동시 실행 최대", peak, "| 결과:", results)
    assert peak == 2


def blocking_io(delay):
    time.sleep(delay)                     # 동기 함수: 이벤트 루프를 멈춘다
    return "블로킹 완료"


async def blocking_trap():
    async def ticker(log):
        for _ in range(3):
            log.append(round(time.perf_counter() - start, 1))
            await asyncio.sleep(0.1)

    log = []
    start = time.perf_counter()
    await asyncio.gather(ticker(log), asyncio.sleep(0), asyncio.to_thread(blocking_io, 0.3))
    print("to_thread로 실행 → 다른 작업이 계속 돈다:", log)

    log2 = []
    start = time.perf_counter()

    async def bad():
        blocking_io(0.3)                  # await 없이 동기 호출
    await asyncio.gather(bad(), ticker(log2))
    print("코루틴 안에서 동기 sleep → 루프가 멈춰 첫 틱이 밀림:", log2)


class AsyncResource:
    async def __aenter__(self):
        await asyncio.sleep(0)
        return self

    async def __aexit__(self, *exc):
        await asyncio.sleep(0)


async def async_gen(n):
    for i in range(n):
        await asyncio.sleep(0)
        yield i


@contextlib.asynccontextmanager
async def session():
    yield "세션"


async def async_protocols():
    async with AsyncResource(), session() as s:
        items = [i async for i in async_gen(3)]
    print("async with / async for:", s, items)


async def main():
    await coroutine_basics()
    await sequential_vs_concurrent()
    await task_group()
    await timeouts()
    await limit_concurrency()
    await blocking_trap()
    await async_protocols()


if __name__ == "__main__":
    asyncio.run(main())
    print("모든 검증 통과")
