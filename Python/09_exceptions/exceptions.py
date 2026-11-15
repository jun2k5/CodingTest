"""09. 예외 심화: 계층, else·finally, 체이닝, ExceptionGroup·except*, add_note, 사용자 예외"""
import warnings


def hierarchy():
    print("KeyError 부모 순서:", [c.__name__ for c in KeyError.__mro__])
    print("KeyboardInterrupt는 Exception인가:", issubclass(KeyboardInterrupt, Exception))
    assert not issubclass(KeyboardInterrupt, Exception)


def flow(value):
    steps = []
    try:
        steps.append("try")
        result = 10 / value
    except ZeroDivisionError:
        steps.append("except")
        result = None
    else:
        steps.append("else")          # 예외가 없을 때만, finally보다 먼저
    finally:
        steps.append("finally")       # 항상
    return steps, result


def return_in_finally_warning():
    src = "def f():\n    try:\n        return 1\n    finally:\n        return 2\n"
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        ns = {}
        exec(compile(src, "<demo>", "exec"), ns)
    print("finally의 return이 이긴다:", ns["f"](), "| 경고:", caught[0].category.__name__ if caught else "없음")
    assert ns["f"]() == 2


class AppError(Exception):
    """애플리케이션 예외의 뿌리"""


class ConfigError(AppError):
    def __init__(self, key, message="설정 누락"):
        super().__init__(f"{message}: {key}")
        self.key = key


def load_config(raw):
    try:
        return int(raw["port"])
    except KeyError as e:
        raise ConfigError("port") from e         # 원인을 명시적으로 연결
    except ValueError:
        raise ConfigError("port", "형식 오류")   # 암묵적 연결(__context__)


def chaining():
    for raw in ({}, {"port": "abc"}):
        try:
            load_config(raw)
        except AppError as e:
            print(f"{type(e).__name__}: {e} | cause={type(e.__cause__).__name__} "
                  f"context={type(e.__context__).__name__} suppress={e.__suppress_context__}")

    try:
        try:
            {}["x"]
        except KeyError:
            raise ValueError("깔끔한 메시지") from None   # 원래 예외 숨기기
    except ValueError as e:
        print("from None:", e.__cause__, e.__suppress_context__)
        assert e.__suppress_context__


def notes_and_groups():
    try:
        try:
            int("x")
        except ValueError as e:
            e.add_note("입력 파일 3번째 줄")             # 3.11+
            raise
    except ValueError as e:
        print("add_note:", e.__notes__)

    errors = ExceptionGroup("검증 실패", [
        ValueError("나이가 음수"),
        TypeError("이름이 문자열 아님"),
        ValueError("이메일 형식"),
    ])
    handled = []
    try:
        raise errors
    except* ValueError as eg:                           # 3.11+
        handled.append(("ValueError", [str(e) for e in eg.exceptions]))
    except* TypeError as eg:
        handled.append(("TypeError", [str(e) for e in eg.exceptions]))
    print("except*:", handled)
    assert handled[0] == ("ValueError", ["나이가 음수", "이메일 형식"])

    sub = errors.subgroup(lambda e: isinstance(e, TypeError))
    print("subgroup:", [str(e) for e in sub.exceptions])


def eafp_vs_lbyl():
    data = {"a": 1}
    # LBYL(Look Before You Leap): 먼저 확인
    lbyl = data["b"] if "b" in data else 0
    # EAFP(Easier to Ask Forgiveness than Permission): 일단 하고 예외 처리 — 파이썬 관례
    try:
        eafp = data["b"]
    except KeyError:
        eafp = 0
    print("LBYL, EAFP:", lbyl, eafp)


if __name__ == "__main__":
    hierarchy()
    print("value=2:", flow(2))
    print("value=0:", flow(0))
    assert flow(2)[0] == ["try", "else", "finally"] and flow(0)[0] == ["try", "except", "finally"]
    return_in_finally_warning()
    chaining()
    notes_and_groups()
    eafp_vs_lbyl()
    print("모든 검증 통과")
