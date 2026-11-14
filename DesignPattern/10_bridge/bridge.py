"""브리지 패턴: 기능 계층(추상)과 구현 계층을 분리해 각각 독립적으로 늘린다.

python bridge.py 로 실행하면 클래스 수 비교와 검증이 나온다.
"""
from abc import ABC, abstractmethod


# 구현 계층 (Implementor): 메시지를 '어디로' 보내는가
class Sender(ABC):
    @abstractmethod
    def send(self, to: str, text: str) -> str: ...


class EmailSender(Sender):
    def send(self, to, text): return f"EMAIL to {to}: {text}"


class SmsSender(Sender):
    def send(self, to, text): return f"SMS to {to}: {text[:20]}"   # SMS는 길이 제한


class SlackSender(Sender):
    def send(self, to, text): return f"SLACK #{to}: {text}"


# 기능 계층 (Abstraction): '무엇을' 보내는가
class Notification:
    def __init__(self, sender: Sender):
        self.sender = sender                   # 브리지: 구현 객체를 참조로 가진다

    def notify(self, to: str, msg: str) -> str:
        return self.sender.send(to, msg)


class UrgentNotification(Notification):        # Refined Abstraction
    def notify(self, to, msg):
        return self.sender.send(to, f"[긴급] {msg}")


class DigestNotification(Notification):
    def __init__(self, sender):
        super().__init__(sender)
        self.buffer: list[str] = []

    def notify(self, to, msg):
        self.buffer.append(msg)
        if len(self.buffer) < 3:
            return ""
        out = self.sender.send(to, " / ".join(self.buffer))
        self.buffer.clear()
        return out


# 비교: 브리지 없이 상속만 쓰면 기능 x 구현 조합마다 클래스가 필요하다
def class_count(n_abstractions, n_implementors):
    inheritance = n_abstractions * n_implementors
    bridge = n_abstractions + n_implementors
    return inheritance, bridge


if __name__ == "__main__":
    senders = [EmailSender(), SmsSender(), SlackSender()]
    for s in senders:
        print(UrgentNotification(s).notify("ops", "디스크 사용량 90% 초과"))
    assert UrgentNotification(SmsSender()).notify("010", "x" * 50) == "SMS to 010: [긴급] " + "x" * 15

    d = DigestNotification(SlackSender())
    outs = [d.notify("dev", f"build #{i}") for i in range(1, 4)]
    print(outs[-1])
    assert outs[:2] == ["", ""] and outs[2] == "SLACK #dev: build #1 / build #2 / build #3"

    # 실행 중에 구현을 바꿀 수 있다
    n = Notification(EmailSender())
    n.sender = SlackSender()
    assert n.notify("x", "y").startswith("SLACK")

    print("기능 3종 x 구현 3종 클래스 수 (상속, 브리지):", class_count(3, 3))
    print("기능 5종 x 구현 6종 클래스 수 (상속, 브리지):", class_count(5, 6))
    assert class_count(5, 6) == (30, 11)
    print("모든 검증 통과")
