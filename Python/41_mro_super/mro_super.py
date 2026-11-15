"""41. MRO와 super(): C3 선형화, 다이아몬드 상속, super()는 '다음 클래스', 협력적 다중 상속, 믹스인"""


class A:
    def hello(self):
        return ["A"]


class B(A):
    def hello(self):
        return ["B"] + super().hello()


class C(A):
    def hello(self):
        return ["C"] + super().hello()


class D(B, C):
    def hello(self):
        return ["D"] + super().hello()


def diamond():
    print("D.__mro__:", [k.__name__ for k in D.__mro__])
    print("D().hello():", D().hello())
    assert D().hello() == ["D", "B", "C", "A"]          # B의 super()는 A가 아니라 C


def super_is_next_in_mro():
    print("B 단독:", B().hello(), "| D 안의 B:", D().hello()[1:])
    print("super(B, D()) → 다음 클래스:", type(super(B, D())).__name__, super(B, D()).hello())


class X:
    pass


class Y:
    pass


def inconsistent_mro():
    class P(X, Y):
        pass

    class Q(Y, X):
        pass
    try:
        class R(P, Q):
            pass
    except TypeError as e:
        print("C3로 순서를 정할 수 없음:", e)


# --- 협력적 다중 상속: **kwargs로 받아서 super()에 넘긴다 ---
class Base:
    def __init__(self, **kwargs):
        if kwargs:
            raise TypeError(f"처리되지 않은 인자: {sorted(kwargs)}")
        self.log = ["Base"]


class Named(Base):
    def __init__(self, *, name, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.log.append("Named")


class Timestamped(Base):
    def __init__(self, *, created="today", **kwargs):
        super().__init__(**kwargs)
        self.created = created
        self.log.append("Timestamped")


class Document(Named, Timestamped):
    def __init__(self, *, title, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.log.append("Document")


def cooperative_init():
    doc = Document(title="보고서", name="kim", created="2026-11-15")
    print("MRO:", [k.__name__ for k in Document.__mro__])
    print("초기화 순서(안쪽부터):", doc.log, "| 값:", doc.title, doc.name, doc.created)
    try:
        Document(title="x", name="y", oops=1)
    except TypeError as e:
        print("남은 인자 감지:", e)


class JsonMixin:
    def to_json(self):
        import json
        return json.dumps({k: v for k, v in vars(self).items() if k != "log"}, ensure_ascii=False)


class ReprMixin:
    def __repr__(self):
        fields = ", ".join(f"{k}={v!r}" for k, v in vars(self).items() if k != "log")
        return f"{type(self).__name__}({fields})"


class Article(JsonMixin, ReprMixin, Document):
    pass


def mixins():
    a = Article(title="파이썬", name="lee")
    print("믹스인:", a.to_json(), "|", repr(a))


if __name__ == "__main__":
    diamond()
    super_is_next_in_mro()
    inconsistent_mro()
    cooperative_init()
    mixins()
    print("모든 검증 통과")
