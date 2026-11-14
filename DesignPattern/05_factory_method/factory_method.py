"""팩토리 메서드 패턴: 객체 생성을 하위 클래스가 정하는 메서드로 미룬다.

python factory_method.py 로 실행하면 검증과 예제 출력이 나온다.
"""
from abc import ABC, abstractmethod


# Product
class Exporter(ABC):
    @abstractmethod
    def export(self, rows: list[dict]) -> str: ...


class CsvExporter(Exporter):
    def export(self, rows):
        header = ",".join(rows[0].keys())
        body = "\n".join(",".join(str(v) for v in r.values()) for r in rows)
        return header + "\n" + body


class JsonExporter(Exporter):
    def export(self, rows):
        import json
        return json.dumps(rows, ensure_ascii=False)


class MarkdownExporter(Exporter):
    def export(self, rows):
        keys = list(rows[0].keys())
        lines = ["| " + " | ".join(keys) + " |", "|" + "---|" * len(keys)]
        lines += ["| " + " | ".join(str(r[k]) for k in keys) + " |" for r in rows]
        return "\n".join(lines)


# Creator: 공통 흐름을 갖고, 무엇을 만들지는 하위 클래스에 맡긴다
class Report(ABC):
    def __init__(self, rows): self.rows = rows

    @abstractmethod
    def create_exporter(self) -> Exporter: ...     # 팩토리 메서드

    def render(self) -> str:
        exporter = self.create_exporter()          # 구체 클래스를 모른다
        return f"[{len(self.rows)} rows]\n" + exporter.export(self.rows)


class CsvReport(Report):
    def create_exporter(self): return CsvExporter()


class JsonReport(Report):
    def create_exporter(self): return JsonExporter()


# 비교: 심플 팩토리 (패턴이 아니라 관용구). 분기를 한 곳에 모은다
def simple_factory(kind: str) -> Exporter:
    if kind == "csv":
        return CsvExporter()
    if kind == "json":
        return JsonExporter()
    raise ValueError(kind)


# 변형: 등록식 팩토리. 새 종류를 추가할 때 팩토리 코드를 고치지 않는다
_registry: dict[str, type[Exporter]] = {}


def register(name: str):
    def deco(cls):
        _registry[name] = cls
        return cls
    return deco


def create(name: str) -> Exporter:
    try:
        return _registry[name]()
    except KeyError:
        raise ValueError(f"unknown exporter: {name}") from None


register("csv")(CsvExporter)
register("json")(JsonExporter)


@register("md")                                   # 새 형식은 데코레이터 한 줄로 등록
class MdExporter(MarkdownExporter):
    pass


if __name__ == "__main__":
    rows = [{"id": 1, "name": "kim"}, {"id": 2, "name": "lee"}]

    csv_out = CsvReport(rows).render()
    json_out = JsonReport(rows).render()
    print(csv_out)
    print(json_out)
    assert csv_out == "[2 rows]\nid,name\n1,kim\n2,lee"
    assert json_out.startswith("[2 rows]\n[{")

    assert isinstance(simple_factory("csv"), CsvExporter)
    assert sorted(_registry) == ["csv", "json", "md"]
    md = create("md").export(rows)
    print(md)
    assert md.splitlines()[0] == "| id | name |"
    try:
        create("xml")
        raise AssertionError
    except ValueError as e:
        print("등록되지 않은 형식:", e)
    print("모든 검증 통과")
