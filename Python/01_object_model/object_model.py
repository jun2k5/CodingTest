"""01. 객체 모델: 이름과 객체, is와 ==, 가변·불변, 얕은 복사와 깊은 복사"""
import copy


def names_and_objects():
    a = [1, 2, 3]
    b = a                      # 새 리스트가 아니라 같은 객체에 이름을 하나 더 붙인다
    b.append(4)
    print("a:", a, "| a is b:", a is b)
    assert a == [1, 2, 3, 4] and a is b

    c = [1, 2, 3, 4]
    print("a == c:", a == c, "| a is c:", a is c)
    assert a == c and a is not c


def immutable_rebinding():
    x = 10
    y = x
    y += 1                     # int는 불변이라 새 객체를 만들고 y만 다시 묶는다
    print("x:", x, "y:", y)
    assert (x, y) == (10, 11)

    s = "ab"
    t = s
    t += "c"
    print("s:", s, "t:", t)
    assert (s, t) == ("ab", "abc")

    lst = [1]
    alias = lst
    alias += [2]               # list의 +=는 제자리 변경(__iadd__)이라 lst도 바뀐다
    print("lst:", lst)
    assert lst == [1, 2]


def argument_passing():
    def append_item(items, value):
        items.append(value)    # 받은 객체를 변경한다 → 호출한 쪽에서도 보인다

    def rebind(items):
        items = [99]           # 지역 이름만 다른 객체로 묶는다 → 호출한 쪽은 그대로
        return items

    data = [1]
    append_item(data, 2)
    rebind(data)
    print("함수 호출 후 data:", data)
    assert data == [1, 2]


def multiplication_trap():
    grid = [[0] * 3] * 3       # 같은 안쪽 리스트를 세 번 참조한다
    grid[0][0] = 1
    print("[[0]*3]*3 변경 후:", grid)
    assert grid == [[1, 0, 0]] * 3

    grid2 = [[0] * 3 for _ in range(3)]
    grid2[0][0] = 1
    print("컴프리헨션 변경 후:", grid2)
    assert grid2 == [[1, 0, 0], [0, 0, 0], [0, 0, 0]]


def shallow_vs_deep():
    original = {"name": "kim", "tags": ["a", "b"]}
    shallow = copy.copy(original)
    deep = copy.deepcopy(original)
    original["tags"].append("c")
    original["name"] = "lee"
    print("shallow:", shallow)
    print("deep   :", deep)
    assert shallow == {"name": "kim", "tags": ["a", "b", "c"]}
    assert deep == {"name": "kim", "tags": ["a", "b"]}
    assert shallow["tags"] is original["tags"] and deep["tags"] is not original["tags"]

    # 다른 얕은 복사 방법들: 슬라이스, 생성자, .copy()
    nested = [[1], [2]]
    for way in (nested[:], list(nested), nested.copy()):
        assert way is not nested and way[0] is nested[0]


def deepcopy_cycle():
    a = [1]
    a.append(a)                # 자기 자신을 담은 리스트
    b = copy.deepcopy(a)       # memo 덕분에 무한 재귀 없이 복사된다
    print("순환 리스트 깊은 복사:", b[1] is b, b is not a)
    assert b[1] is b and b is not a


def tuple_with_list():
    t = ([1], 2)
    try:
        t[0] += [3]            # 리스트는 바뀌지만 튜플 항목 대입에서 TypeError
    except TypeError as e:
        print("TypeError:", e)
    print("그래도 바뀐 t:", t)
    assert t == ([1, 3], 2)


if __name__ == "__main__":
    names_and_objects()
    immutable_rebinding()
    argument_passing()
    multiplication_trap()
    shallow_vs_deep()
    deepcopy_cycle()
    tuple_with_list()
    print("모든 검증 통과")
