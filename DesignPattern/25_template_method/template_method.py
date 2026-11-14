"""템플릿 메서드 패턴: 알고리즘의 뼈대는 상위 클래스에 두고, 일부 단계만 하위 클래스가 바꾼다.

python template_method.py 로 실행하면 검증과 예제 출력이 나온다.
"""
from abc import ABC, abstractmethod
import csv
import io
import json


class DataImporter(ABC):
    def run(self, raw: str) -> dict:                 # 템플릿 메서드: 순서를 고정한다
        records = self.parse(raw)                    # 추상 단계 (반드시 구현)
        records = [r for r in records if self.is_valid(r)]
        records = [self.transform(r) for r in records]
        self.before_save(records)                    # 훅 (선택적으로 재정의)
        return {"saved": len(records), "rows": records}

    @abstractmethod
    def parse(self, raw: str) -> list[dict]: ...

    def is_valid(self, r: dict) -> bool:             # 기본 구현이 있는 단계
        return bool(r.get("email")) and "@" in r["email"]

    def transform(self, r: dict) -> dict:
        return {"email": r["email"].strip().lower(), "name": r.get("name", "").strip()}

    def before_save(self, records: list[dict]) -> None:   # 훅: 기본은 아무것도 안 함
        pass


class CsvImporter(DataImporter):
    def parse(self, raw):
        return list(csv.DictReader(io.StringIO(raw)))


class JsonImporter(DataImporter):
    def parse(self, raw):
        return json.loads(raw)


class DedupJsonImporter(JsonImporter):
    """훅을 재정의해 중복 이메일을 제거한다."""
    def before_save(self, records):
        seen, out = set(), []
        for r in records:
            if r["email"] not in seen:
                seen.add(r["email"])
                out.append(r)
        records[:] = out


# 비교: 같은 일을 전략(합성)으로. 단계를 함수로 넘긴다
def run_with(parse, raw, is_valid=lambda r: "@" in r.get("email", "")):
    return [r for r in parse(raw) if is_valid(r)]


if __name__ == "__main__":
    csv_raw = "email,name\nKim@Example.com , kim\nbad-email,lee\npark@example.com,park\n"
    json_raw = json.dumps([
        {"email": "A@x.com", "name": "a"},
        {"email": "a@x.com ", "name": "a2"},
        {"email": "", "name": "none"},
        {"email": "b@x.com", "name": "b"},
    ])

    r1 = CsvImporter().run(csv_raw)
    r2 = JsonImporter().run(json_raw)
    r3 = DedupJsonImporter().run(json_raw)
    print("CSV        :", r1["saved"], [r["email"] for r in r1["rows"]])
    print("JSON       :", r2["saved"], [r["email"] for r in r2["rows"]])
    print("JSON+dedup :", r3["saved"], [r["email"] for r in r3["rows"]])
    assert r1["saved"] == 2 and r1["rows"][0]["email"] == "kim@example.com"
    assert r2["saved"] == 3 and r3["saved"] == 2

    try:
        DataImporter()
        raise AssertionError
    except TypeError:
        print("추상 단계(parse)를 구현하지 않은 클래스는 인스턴스를 만들 수 없다")

    assert len(run_with(json.loads, json_raw)) == 3
    print("모든 검증 통과")
