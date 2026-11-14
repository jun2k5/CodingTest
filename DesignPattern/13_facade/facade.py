"""퍼사드 패턴: 복잡한 하위 시스템 앞에 단순한 창구 하나를 둔다.

python facade.py 로 실행하면 검증과 예제 출력이 나온다.
"""


# 하위 시스템들: 각자 자기 일만 알고, 호출 순서는 모른다
class Inventory:
    def __init__(self): self.stock = {"book": 3, "pen": 0}
    def reserve(self, item, qty):
        if self.stock.get(item, 0) < qty:
            raise ValueError(f"재고 부족: {item}")
        self.stock[item] -= qty
    def release(self, item, qty): self.stock[item] += qty


class PaymentService:
    def __init__(self): self.charged = []
    def charge(self, user, amount):
        if amount > 100_000:
            raise ValueError("한도 초과")
        self.charged.append((user, amount))
        return f"pay-{len(self.charged)}"
    def refund(self, pay_id): self.charged.pop()


class Shipping:
    def __init__(self): self.queue = []
    def schedule(self, user, item): self.queue.append((user, item)); return f"ship-{len(self.queue)}"


class Mailer:
    def __init__(self): self.outbox = []
    def send(self, to, text): self.outbox.append((to, text))


PRICES = {"book": 18_000, "pen": 1_500, "laptop": 1_500_000}


# 퍼사드: 순서·보상(롤백)·예외 처리를 한 곳에 모은다
class OrderFacade:
    def __init__(self, inventory, payment, shipping, mailer):
        self.inventory, self.payment = inventory, payment
        self.shipping, self.mailer = shipping, mailer

    def place_order(self, user: str, item: str, qty: int) -> str:
        self.inventory.reserve(item, qty)
        try:
            pay_id = self.payment.charge(user, PRICES[item] * qty)
        except ValueError:
            self.inventory.release(item, qty)            # 결제 실패 -> 재고 원복
            raise
        ship_id = self.shipping.schedule(user, item)
        self.mailer.send(user, f"{item} x{qty} 주문 완료 ({pay_id}, {ship_id})")
        return ship_id


if __name__ == "__main__":
    inv, pay, ship, mail = Inventory(), PaymentService(), Shipping(), Mailer()
    shop = OrderFacade(inv, pay, ship, mail)

    print(shop.place_order("kim", "book", 2))
    assert inv.stock["book"] == 1 and pay.charged == [("kim", 36_000)]
    print(mail.outbox[-1])

    for item, qty in [("pen", 1), ("book", 5)]:
        try:
            shop.place_order("lee", item, qty)
            raise AssertionError
        except ValueError as e:
            print("주문 실패:", e)

    inv.stock["laptop"] = 1
    try:
        shop.place_order("park", "laptop", 1)
        raise AssertionError
    except ValueError as e:
        print("주문 실패:", e, "| laptop 재고", inv.stock["laptop"])
    assert inv.stock["laptop"] == 1                      # 롤백 확인
    assert len(ship.queue) == 1 and len(mail.outbox) == 1

    # 하위 시스템은 여전히 직접 쓸 수 있다 (퍼사드는 막지 않는다)
    inv.reserve("book", 1)
    assert inv.stock["book"] == 0
    print("모든 검증 통과")
