"""29. json·pickle·csv: 타입 대응, 커스텀 인코더·디코더, pickle 보안, csv 방언·DictReader"""
import csv
import hmac
import hashlib
import io
import json
import pickle
import secrets
from dataclasses import asdict, dataclass
from datetime import date, datetime
from decimal import Decimal


def json_basics():
    data = {"name": "김", "tags": ("a", "b"), 1: True, "none": None, "f": 1.5}
    text = json.dumps(data, ensure_ascii=False)
    print("dumps:", text)
    back = json.loads(text)
    print("loads 후 바뀐 것: 튜플→", type(back["tags"]).__name__, "| 키 1→", repr(list(back)[2]))
    print("ensure_ascii=True(기본):", json.dumps("김"))
    print("indent·sort_keys:", json.dumps({"b": 1, "a": [1, 2]}, indent=2, sort_keys=True).replace("\n", "⏎"))
    try:
        json.dumps({"d": date(2026, 1, 1)})
    except TypeError as e:
        print("기본으로 안 되는 타입:", e)


@dataclass
class Order:
    id: int
    ordered: date
    amount: Decimal


class AppEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (date, datetime)):
            return o.isoformat()
        if isinstance(o, Decimal):
            return str(o)
        if hasattr(o, "__dataclass_fields__"):
            return asdict(o)
        return super().default(o)


def decode_hook(d):
    if "ordered" in d:
        d["ordered"] = date.fromisoformat(d["ordered"])
    if "amount" in d:
        d["amount"] = Decimal(d["amount"])
    return d


def json_custom():
    order = Order(1, date(2026, 11, 15), Decimal("19.90"))
    text = json.dumps(order, cls=AppEncoder, ensure_ascii=False)
    print("커스텀 인코더:", text)
    restored = Order(**json.loads(text, object_hook=decode_hook))
    print("object_hook 복원:", restored, "| 같은가:", restored == order)
    print("float로 읽으면 오차 가능, parse_float=Decimal:", json.loads("0.1", parse_float=Decimal))
    assert restored == order


class Evil:
    def __reduce__(self):                       # 역직렬화 때 호출할 함수와 인자를 지정
        return (print, ("!!! 역직렬화 중 임의 코드 실행됨 !!!",))


def pickle_demo():
    obj = {"set": {1, 2}, "date": date(2026, 1, 1), "order": Order(2, date(2026, 1, 2), Decimal("1"))}
    blob = pickle.dumps(obj)
    print("pickle 왕복(파이썬 객체 그대로):", pickle.loads(blob) == obj, "| 크기:", len(blob) > 0)

    payload = pickle.dumps(Evil())
    print("악성 pickle 로드:")
    pickle.loads(payload)                        # 신뢰할 수 없는 데이터에 절대 쓰면 안 되는 이유

    key = secrets.token_bytes(32)
    sig = hmac.new(key, blob, hashlib.sha256).digest()
    ok = hmac.compare_digest(sig, hmac.new(key, blob, hashlib.sha256).digest())
    tampered = hmac.compare_digest(sig, hmac.new(key, blob + b"x", hashlib.sha256).digest())
    print("HMAC 서명 검증:", ok, "| 변조 감지:", not tampered)


def csv_demo():
    rows = [{"name": "kim", "memo": "쉼표, 포함", "score": 90},
            {"name": "lee", "memo": '따옴표 "있음"', "score": 85}]
    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=["name", "memo", "score"])
    writer.writeheader()
    writer.writerows(rows)
    text = buf.getvalue()
    print("DictWriter 결과:")
    for line in text.splitlines():
        print("  " + line)

    reader = csv.DictReader(io.StringIO(text, newline=""))
    loaded = list(reader)
    print("DictReader:", loaded[0], "| score 타입:", type(loaded[0]["score"]).__name__)
    assert loaded[1]["memo"] == '따옴표 "있음"'

    tsv = "a\tb\n1\t2\n"
    print("구분자 지정(TSV):", list(csv.reader(io.StringIO(tsv), delimiter="\t")))
    dialect = csv.Sniffer().sniff("x;y;z\n1;2;3\n")
    print("Sniffer 추측 구분자:", repr(dialect.delimiter))


if __name__ == "__main__":
    json_basics()
    json_custom()
    pickle_demo()
    csv_demo()
    print("모든 검증 통과")
