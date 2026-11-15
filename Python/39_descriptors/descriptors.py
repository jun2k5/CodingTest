"""39. 디스크립터와 property: __get__·__set__·__set_name__, 데이터·비데이터 디스크립터 우선순위, 메서드 바인딩"""


class Positive:
    """검증 디스크립터: 클래스 속성으로 두면 인스턴스 속성 접근을 가로챈다"""

    def __set_name__(self, owner, name):     # 3.6+: 어떤 이름으로 붙었는지 알려 준다
        self.public = name
        self.private = "_" + name

    def __get__(self, obj, objtype=None):
        if obj is None:                      # 클래스에서 접근하면 디스크립터 자신
            return self
        return getattr(obj, self.private)

    def __set__(self, obj, value):
        if value <= 0:
            raise ValueError(f"{self.public}은(는) 양수여야 함: {value}")
        setattr(obj, self.private, value)


class Product:
    price = Positive()
    stock = Positive()

    def __init__(self, price, stock):
        self.price = price                  # Positive.__set__ 호출
        self.stock = stock


def validation_descriptor():
    p = Product(1000, 3)
    print("값:", p.price, p.stock, "| 실제 저장:", vars(p))
    try:
        p.stock = -1
    except ValueError as e:
        print("검증:", e)
    print("클래스에서 접근:", type(Product.price).__name__)


class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    @property
    def fahrenheit(self):
        return self.celsius * 9 / 5 + 32

    @fahrenheit.setter
    def fahrenheit(self, value):
        self.celsius = (value - 32) * 5 / 9


def property_is_descriptor():
    t = Temperature(100)
    print("property get:", t.fahrenheit)
    t.fahrenheit = 32
    print("property set 후 celsius:", t.celsius)
    print("property는 디스크립터:", hasattr(property, "__get__"), hasattr(property, "__set__"))
    try:
        t.__dict__["fahrenheit"] = 999      # 인스턴스 dict에 같은 이름을 넣어도
        print("데이터 디스크립터가 이긴다:", t.fahrenheit)
    finally:
        del t.__dict__["fahrenheit"]


class Lazy:
    """비데이터 디스크립터(__get__만): 인스턴스 dict에 같은 이름이 생기면 그쪽이 이긴다"""

    def __init__(self, func):
        self.func = func
        self.name = func.__name__

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        value = self.func(obj)
        obj.__dict__[self.name] = value     # 다음부터는 인스턴스 속성이 바로 찾아짐
        return value


class Report:
    calls = 0

    @Lazy
    def total(self):
        Report.calls += 1
        return sum(range(1000))


def non_data_descriptor():
    r = Report()
    print("Lazy:", r.total, r.total, "| 계산 횟수:", Report.calls, "| dict에 저장됨:", "total" in vars(r))
    assert Report.calls == 1


class Greeter:
    def hello(self, name):
        return f"hello {name} from {type(self).__name__}"

    @staticmethod
    def static(x):
        return x * 2

    @classmethod
    def create(cls):
        return cls()


def method_binding():
    g = Greeter()
    func = Greeter.__dict__["hello"]
    print("클래스 dict의 함수:", type(func).__name__)
    bound = func.__get__(g, Greeter)         # g.hello가 내부에서 하는 일
    print("__get__으로 바인딩:", type(bound).__name__, bound("kim"))
    print("g.hello is 같은 객체?:", g.hello is g.hello, "| __self__:", g.hello.__self__ is g)
    print("staticmethod:", Greeter.static(3), "| classmethod:", type(Greeter.create()).__name__)
    print("함수에 __get__ 있음:", hasattr(func, "__get__"), "| 비데이터:", not hasattr(func, "__set__"))


if __name__ == "__main__":
    validation_descriptor()
    property_is_descriptor()
    non_data_descriptor()
    method_binding()
    print("모든 검증 통과")
