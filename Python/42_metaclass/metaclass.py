"""42. 클래스 생성과 메타클래스: 클래스도 객체, type(name, bases, ns), class 문의 실행 과정,
__init_subclass__, __set_name__, 메타클래스가 정말 필요한 경우"""


def classes_are_objects():
    class Dog:
        sound = "멍"

        def speak(self):
            return self.sound

    print("type(Dog):", type(Dog).__name__, "| type(type):", type(type).__name__)
    Cat = type("Cat", (Dog,), {"sound": "야옹"})        # class 문 없이 클래스 만들기
    print("type()으로 만든 클래스:", Cat.__name__, Cat.__mro__[1].__name__, Cat().speak())


def class_statement_steps():
    order = []

    class Meta(type):
        @classmethod
        def __prepare__(mcls, name, bases):
            order.append("1. __prepare__: 네임스페이스 dict 준비")
            return {}

        def __new__(mcls, name, bases, ns):
            order.append(f"3. Meta.__new__: 몸체 실행 결과로 클래스 생성 ({sorted(k for k in ns if not k.startswith('__'))})")
            return super().__new__(mcls, name, bases, ns)

        def __init__(cls, name, bases, ns):
            order.append("4. Meta.__init__")
            super().__init__(name, bases, ns)

    class Demo(metaclass=Meta):
        order.append("2. 클래스 몸체 실행")
        x = 1

        def m(self):
            pass

    for step in order:
        print("  " + step)


class Plugin:
    registry = {}

    def __init_subclass__(cls, /, key=None, **kwargs):       # 3.6+: 메타클래스 없이 하위 클래스 훅
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "run"):
            raise TypeError(f"{cls.__name__}에 run()이 없다")
        Plugin.registry[key or cls.__name__.lower()] = cls


class CsvExport(Plugin, key="csv"):
    def run(self):
        return "CSV 내보내기"


class JsonExport(Plugin):
    def run(self):
        return "JSON 내보내기"


def init_subclass_demo():
    print("자동 등록:", sorted(Plugin.registry), "|", Plugin.registry["csv"]().run())
    try:
        class Broken(Plugin):
            pass
    except TypeError as e:
        print("정의 시점 검증:", e)


class Field:
    def __set_name__(self, owner, name):
        self.name = name
        owner.fields = getattr(owner, "fields", ()) + (name,)

    def __get__(self, obj, objtype=None):
        return self if obj is None else obj.__dict__.get(self.name)

    def __set__(self, obj, value):
        obj.__dict__[self.name] = value


class Model:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if k not in self.fields:
                raise TypeError(f"알 수 없는 필드 {k}")
            setattr(self, k, v)


class User(Model):
    name = Field()
    email = Field()


def set_name_demo():
    u = User(name="kim", email="k@test.com")
    print("__set_name__로 모은 필드:", User.fields, "| 값:", u.name, u.email)


class SingletonMeta(type):
    """메타클래스가 맞는 드문 예: 클래스 '호출'(인스턴스 생성) 자체를 바꾸기"""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class AppConfig(metaclass=SingletonMeta):
    def __init__(self):
        self.loaded = True


def metaclass_call():
    print("메타클래스 __call__:", AppConfig() is AppConfig(), "| 메타클래스:", type(AppConfig).__name__)


if __name__ == "__main__":
    classes_are_objects()
    print("class 문 실행 순서:")
    class_statement_steps()
    init_subclass_demo()
    set_name_demo()
    metaclass_call()
    assert set(Plugin.registry) == {"csv", "jsonexport"}
    print("모든 검증 통과")
