"""UML 클래스 다이어그램의 관계 6가지를 코드로 옮긴 예.

python uml_relations.py 로 실행하면 각 관계의 생명주기 차이를 확인한다.
"""
from abc import ABC, abstractmethod
import gc
import weakref


# 실현(Realization): 인터페이스를 구현한다      Flyable <|.. Bird
class Flyable(ABC):
    @abstractmethod
    def fly(self) -> str: ...


# 일반화(Generalization): 상속                  Animal <|-- Bird
class Animal:
    def __init__(self, name): self.name = name


class Bird(Animal, Flyable):
    def fly(self): return f"{self.name} flies"


# 의존(Dependency): 메서드 안에서 잠깐 쓴다      Zookeeper ..> Food
class Food:
    def __init__(self, kind): self.kind = kind


class Zookeeper:
    def feed(self, animal: Animal, food: Food) -> str:   # 매개변수로만 쓰고 보관하지 않는다
        return f"{animal.name} eats {food.kind}"


# 연관(Association): 필드로 계속 참조한다        Student --> Course
class Course:
    def __init__(self, title): self.title = title


class Student:
    def __init__(self, name):
        self.name = name
        self.courses: list[Course] = []


# 집약(Aggregation): 전체-부분, 부분은 독립적으로 산다   Team o-- Player
class Player:
    def __init__(self, name): self.name = name


class Team:
    def __init__(self, players: list[Player]):
        self.players = players            # 밖에서 만든 객체를 받는다


# 합성(Composition): 전체가 부분의 생명주기를 책임진다   House *-- Room
class Room:
    def __init__(self, name): self.name = name


class House:
    def __init__(self, room_names: list[str]):
        self.rooms = [Room(n) for n in room_names]   # 안에서 직접 만든다


if __name__ == "__main__":
    b = Bird("sparrow")
    assert isinstance(b, Animal) and isinstance(b, Flyable)
    print("일반화·실현:", b.fly())

    print("의존:", Zookeeper().feed(b, Food("seed")))

    s = Student("kim")
    s.courses.append(Course("DB"))
    print("연관:", s.name, "->", [c.title for c in s.courses])

    p = Player("lee")
    team = Team([p])
    ref_player = weakref.ref(p)
    del team
    gc.collect()
    assert ref_player() is not None       # 팀이 사라져도 선수는 남는다
    print("집약: Team 삭제 후 Player 생존 =", ref_player() is not None)

    h = House(["kitchen", "bedroom"])
    ref_room = weakref.ref(h.rooms[0])
    del h
    gc.collect()
    assert ref_room() is None             # 집이 사라지면 방도 사라진다
    print("합성: House 삭제 후 Room 생존 =", ref_room() is not None)
    print("모든 검증 통과")
