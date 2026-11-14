"""어댑터 패턴: 호환되지 않는 인터페이스를 클라이언트가 기대하는 인터페이스로 바꾼다.

python adapter.py 로 실행하면 검증과 예제 출력이 나온다.
"""
from abc import ABC, abstractmethod
import xml.etree.ElementTree as ET


# Target: 우리 코드가 기대하는 인터페이스
class PaymentGateway(ABC):
    @abstractmethod
    def pay(self, order_id: str, amount_won: int) -> dict: ...


# Adaptee 1: 금액을 '센트 단위 달러'로 받고 결과를 튜플로 주는 외부 SDK (고칠 수 없다)
class GlobalPaySDK:
    RATE = 1400                              # 1달러 = 1400원 가정

    def make_charge(self, cents: int, reference: str):
        return ("OK", f"gp-{reference}", cents)


# Adaptee 2: 결과를 XML 문자열로 주는 레거시 모듈
class LegacyPay:
    def request(self, xml_body: str) -> str:
        root = ET.fromstring(xml_body)
        oid, amt = root.findtext("order"), root.findtext("amount")
        return f"<result><code>0000</code><tid>lg-{oid}</tid><amount>{amt}</amount></result>"


# 객체 어댑터: Adaptee를 필드로 가지고 Target을 구현한다 (합성)
class GlobalPayAdapter(PaymentGateway):
    def __init__(self, sdk: GlobalPaySDK):
        self.sdk = sdk

    def pay(self, order_id, amount_won):
        cents = round(amount_won / GlobalPaySDK.RATE * 100)
        status, tx, charged = self.sdk.make_charge(cents, order_id)
        return {"ok": status == "OK", "tx_id": tx, "amount_won": round(charged / 100 * GlobalPaySDK.RATE)}


class LegacyPayAdapter(PaymentGateway):
    def __init__(self, legacy: LegacyPay):
        self.legacy = legacy

    def pay(self, order_id, amount_won):
        body = f"<pay><order>{order_id}</order><amount>{amount_won}</amount></pay>"
        res = ET.fromstring(self.legacy.request(body))
        return {"ok": res.findtext("code") == "0000", "tx_id": res.findtext("tid"),
                "amount_won": int(res.findtext("amount"))}


# 클래스 어댑터: Target과 Adaptee를 다중 상속한다 (Python·C++에서 가능, Java는 불가)
class GlobalPayClassAdapter(PaymentGateway, GlobalPaySDK):
    def pay(self, order_id, amount_won):
        cents = round(amount_won / self.RATE * 100)
        status, tx, charged = self.make_charge(cents, order_id)
        return {"ok": status == "OK", "tx_id": tx, "amount_won": round(charged / 100 * self.RATE)}


# 클라이언트: PaymentGateway만 안다
def checkout(gateway: PaymentGateway, order_id: str, amount: int) -> str:
    r = gateway.pay(order_id, amount)
    return f"{order_id}: {'성공' if r['ok'] else '실패'} ({r['tx_id']}, {r['amount_won']}원)"


if __name__ == "__main__":
    gateways = [GlobalPayAdapter(GlobalPaySDK()), LegacyPayAdapter(LegacyPay()), GlobalPayClassAdapter()]
    for g in gateways:
        line = checkout(g, "A100", 28000)
        print(type(g).__name__, "->", line)
        assert "성공" in line and "28000원" in line
    print("모든 검증 통과")
