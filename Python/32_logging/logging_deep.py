"""32. logging 심화: 로거 계층과 전파, 레벨, 핸들러·포매터, 지연 포매팅, exception, dictConfig, 필터, 회전 파일"""
import io
import logging
import logging.config
import logging.handlers
import tempfile
from pathlib import Path


def hierarchy():
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(logging.WARNING)

    app = logging.getLogger("app")
    db = logging.getLogger("app.db")
    app.setLevel(logging.DEBUG)
    db.debug("app.db의 DEBUG: 자기 레벨은 NOTSET → 부모 app의 DEBUG를 따름")
    db.info("전파되어 루트 핸들러가 출력")
    logging.getLogger("other").info("other는 루트 레벨 WARNING이라 버려짐")
    logging.getLogger("other").warning("other WARNING은 출력")
    print("부모:", db.parent.name, "| 같은 이름은 같은 객체:", logging.getLogger("app.db") is db)
    print("출력된 줄:")
    for line in stream.getvalue().splitlines():
        print("  " + line)


def handlers_and_propagate():
    out_all, out_err = io.StringIO(), io.StringIO()
    logger = logging.getLogger("svc")
    logger.handlers.clear()
    logger.setLevel(logging.DEBUG)
    logger.propagate = False                      # 루트로 올려보내지 않음(중복 출력 방지)
    h_all = logging.StreamHandler(out_all)
    h_err = logging.StreamHandler(out_err)
    h_err.setLevel(logging.ERROR)                 # 핸들러별 레벨
    fmt = logging.Formatter("[%(levelname)s] %(funcName)s:%(lineno)d %(message)s")
    for h in (h_all, h_err):
        h.setFormatter(fmt)
        logger.addHandler(h)
    logger.info("주문 생성 id=%s", 42)              # 지연 포매팅: 출력될 때만 문자열을 만든다
    logger.error("결제 실패 id=%s", 42)
    print("전체 핸들러 줄 수:", len(out_all.getvalue().splitlines()), "| 에러 핸들러:", out_err.getvalue().strip())


def lazy_and_exception():
    stream = io.StringIO()
    logger = logging.getLogger("lazy")
    logger.handlers[:] = [logging.StreamHandler(stream)]
    logger.propagate = False
    logger.setLevel(logging.INFO)

    class Expensive:
        calls = 0

        def __str__(self):
            Expensive.calls += 1
            return "비싼 문자열"
    logger.debug("값: %s", Expensive())           # DEBUG는 버려지므로 __str__ 호출 안 됨
    print("버려진 로그에서 __str__ 호출:", Expensive.calls)
    print("isEnabledFor(DEBUG):", logger.isEnabledFor(logging.DEBUG))

    try:
        1 / 0
    except ZeroDivisionError:
        logger.exception("계산 실패")              # ERROR 레벨 + 트레이스백
    text = stream.getvalue()
    print("exception()이 트레이스백 포함:", "Traceback" in text and "ZeroDivisionError" in text)


class RequestIdFilter(logging.Filter):
    def __init__(self, request_id):
        super().__init__()
        self.request_id = request_id

    def filter(self, record):
        record.request_id = self.request_id        # 레코드에 필드 추가
        return True


def dict_config_and_filter():
    stream = io.StringIO()
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {"simple": {"format": "%(asctime)s %(levelname)s [%(request_id)s] %(message)s",
                                  "datefmt": "%H:%M:%S"}},
        "handlers": {"mem": {"class": "logging.StreamHandler", "stream": stream, "formatter": "simple"}},
        "loggers": {"web": {"level": "INFO", "handlers": ["mem"], "propagate": False}},
    })
    web = logging.getLogger("web")
    web.addFilter(RequestIdFilter("req-7f3"))
    web.info("GET /users")
    line = stream.getvalue().strip()
    print("dictConfig + 필터:", line.split(" ", 1)[1])
    assert "[req-7f3]" in line


def rotating():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "app.log"
        logger = logging.getLogger("rot")
        logger.propagate = False
        h = logging.handlers.RotatingFileHandler(path, maxBytes=200, backupCount=2, encoding="utf-8")
        logger.handlers[:] = [h]
        logger.setLevel(logging.INFO)
        for i in range(30):
            logger.info("줄 %02d 회전 테스트 메시지", i)
        h.close()
        print("회전 파일 목록:", sorted(p.name for p in Path(tmp).iterdir()))


if __name__ == "__main__":
    hierarchy()
    handlers_and_propagate()
    lazy_and_exception()
    dict_config_and_filter()
    rotating()
    print("모든 검증 통과")
