"""10편: 로컬 PostgreSQL 앞에 두는 지연 주입 TCP 프록시.

같은 PC의 Docker PostgreSQL은 왕복 시간이 거의 0이라, RDS처럼 네트워크 너머에 있는 DB의
"쿼리 수 × 왕복 시간" 비용이 드러나지 않는다. 이 프록시는 양방향 데이터를 각각 delay_ms만큼
늦게 전달한다(순서는 유지, 처리량은 제한하지 않음). 왕복 시간은 약 2 × delay_ms가 된다.

사용: python tools/latency_proxy.py --listen 54330 --target 54329 --delay-ms 1
"""
import argparse
import asyncio
import threading
import time


async def _pipe(reader, writer, delay: float):
    queue: asyncio.Queue = asyncio.Queue()

    async def send():
        while True:
            due, data = await queue.get()
            if data is None:
                break
            # Windows의 asyncio.sleep은 해상도가 약 15ms라 짧은 지연이 크게 부풀려진다.
            # 남은 시간이 20ms 이하이면 sleep(0)으로 양보하며 기다린다(CPU를 쓰지만 정확하다).
            wait = due - time.perf_counter()
            if wait > 0.02:
                await asyncio.sleep(wait - 0.02)
            while time.perf_counter() < due:
                await asyncio.sleep(0)
            writer.write(data)
            await writer.drain()
        writer.close()

    sender = asyncio.create_task(send())
    try:
        while data := await reader.read(65536):
            queue.put_nowait((time.perf_counter() + delay, data))
    finally:
        queue.put_nowait((0, None))
        await sender


async def _handle(client_r, client_w, target_port: int, delay: float):
    server_r, server_w = await asyncio.open_connection("127.0.0.1", target_port)
    await asyncio.gather(_pipe(client_r, server_w, delay), _pipe(server_r, client_w, delay),
                         return_exceptions=True)


async def serve(listen: int, target: int, delay_ms: float, ready: threading.Event | None = None):
    server = await asyncio.start_server(
        lambda r, w: _handle(r, w, target, delay_ms / 1000), "127.0.0.1", listen)
    if ready:
        ready.set()
    async with server:
        await server.serve_forever()


def start_in_thread(listen: int, target: int, delay_ms: float) -> None:
    """테스트용: 데몬 스레드에서 프록시를 띄운다."""
    ready = threading.Event()
    threading.Thread(target=lambda: asyncio.run(serve(listen, target, delay_ms, ready)),
                     daemon=True).start()
    assert ready.wait(5)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--listen", type=int, default=54330)
    ap.add_argument("--target", type=int, default=54329)
    ap.add_argument("--delay-ms", type=float, default=1.0)
    a = ap.parse_args()
    asyncio.run(serve(a.listen, a.target, a.delay_ms))
