"""33. unittest.mock과 테스트 도구: TestCase, Mock·MagicMock, return_value·side_effect, patch, spec, assert_called"""
import io
import unittest
from datetime import datetime
from unittest import mock


# --- 테스트 대상 코드 ---
def fetch_user(client, user_id):
    resp = client.get(f"/users/{user_id}")
    if resp.status_code == 404:
        return None
    return resp.json()["name"]


def greeting():
    hour = datetime.now().hour
    return "좋은 아침" if hour < 12 else "좋은 오후"


class PaymentGateway:
    def charge(self, amount):
        raise RuntimeError("실제 결제 API를 호출하면 안 된다")


def checkout(gateway, amount, retries=2):
    for attempt in range(retries + 1):
        try:
            return gateway.charge(amount)
        except TimeoutError:
            if attempt == retries:
                raise


# --- 테스트 ---
REAL_DATETIME = datetime          # patch 전에 진짜 클래스를 잡아 둔다
class FetchUserTest(unittest.TestCase):
    def test_returns_name(self):
        client = mock.Mock()
        client.get.return_value.status_code = 200
        client.get.return_value.json.return_value = {"name": "kim"}
        self.assertEqual(fetch_user(client, 7), "kim")
        client.get.assert_called_once_with("/users/7")

    def test_404_returns_none(self):
        client = mock.Mock()
        client.get.return_value.status_code = 404
        self.assertIsNone(fetch_user(client, 99))


class GreetingTest(unittest.TestCase):
    @mock.patch(f"{__name__}.datetime")            # '사용되는 곳'의 이름을 바꾼다
    def test_morning(self, fake_dt):
        fake_dt.now.return_value = REAL_DATETIME(2026, 11, 15, 9, 0)
        self.assertEqual(greeting(), "좋은 아침")

    def test_afternoon_with_context_manager(self):
        with mock.patch(f"{__name__}.datetime") as fake_dt:
            fake_dt.now.return_value = REAL_DATETIME(2026, 11, 15, 15, 0)
            self.assertEqual(greeting(), "좋은 오후")


class CheckoutTest(unittest.TestCase):
    def test_retry_then_success(self):
        gw = mock.create_autospec(PaymentGateway, instance=True)
        gw.charge.side_effect = [TimeoutError, TimeoutError, "승인"]     # 호출마다 다른 결과
        self.assertEqual(checkout(gw, 1000), "승인")
        self.assertEqual(gw.charge.call_count, 3)
        gw.charge.assert_has_calls([mock.call(1000)] * 3)

    def test_gives_up(self):
        gw = mock.create_autospec(PaymentGateway, instance=True)
        gw.charge.side_effect = TimeoutError
        with self.assertRaises(TimeoutError):
            checkout(gw, 1000)

    def test_autospec_catches_wrong_signature(self):
        gw = mock.create_autospec(PaymentGateway, instance=True)
        with self.assertRaises(TypeError):
            gw.charge(1000, "추가 인자")             # 실제 시그니처와 다르면 실패

    def test_patch_object(self):
        with mock.patch.object(PaymentGateway, "charge", return_value="모의 승인") as m:
            self.assertEqual(checkout(PaymentGateway(), 500), "모의 승인")
            m.assert_called_once_with(500)


class MockBehaviorTest(unittest.TestCase):
    def test_mock_accepts_anything(self):
        m = mock.Mock()
        m.anything.you.like(1, 2)                     # 오타도 그냥 통과한다
        self.assertTrue(m.anything.you.like.called)
        with self.assertRaises(AttributeError):       # assert 오타(assrt, assret 등)는 막아 준다
            m.assrt_called_once()

    def test_magicmock_supports_dunder(self):
        mm = mock.MagicMock()
        mm.__len__.return_value = 3
        mm.__getitem__.side_effect = lambda k: k * 2
        self.assertEqual((len(mm), mm[5]), (3, 10))

    def test_mock_open(self):
        m = mock.mock_open(read_data="line1\nline2\n")
        with mock.patch("builtins.open", m):
            with open("아무파일.txt", encoding="utf-8") as f:
                self.assertEqual(f.read().splitlines(), ["line1", "line2"])
        m.assert_called_once_with("아무파일.txt", encoding="utf-8")


if __name__ == "__main__":
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromModule(__import__("__main__")))
    for line in stream.getvalue().splitlines():
        if line.endswith(("ok", "ERROR", "FAIL")):
            print(line)
    print(f"실행 {result.testsRun}개, 실패 {len(result.failures)}, 오류 {len(result.errors)}")
    assert result.wasSuccessful()
    print("모든 검증 통과")
