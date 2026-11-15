"""12. Counter: 다중집합, most_common, total, update/subtract, 산술·집합 연산"""
from collections import Counter

TEXT = "the quick brown fox jumps over the lazy dog the end"


def basics():
    c = Counter(TEXT.split())
    print("most_common(2):", c.most_common(2))
    print("없는 키는 0:", c["cat"], "| 키 생기지 않음:", "cat" in c)
    assert c["cat"] == 0 and "cat" not in c
    print("total():", c.total(), "| 서로 다른 단어:", len(c))   # total: 3.10+
    assert c.total() == len(TEXT.split())

    letters = Counter("mississippi")
    print("문자 카운트:", letters)
    print("elements():", "".join(sorted(letters.elements())))


def update_subtract():
    stock = Counter(apple=3, pear=1)
    stock.update(["apple", "kiwi"])         # 이터러블이면 원소마다 +1
    stock.update({"pear": 5})               # 매핑이면 값만큼 더함
    print("update 후:", stock)
    stock.subtract(apple=10)
    print("subtract 후(음수 허용):", stock)
    assert stock["apple"] == -6


def arithmetic():
    a = Counter(x=3, y=1)
    b = Counter(x=1, y=2, z=1)
    print("a + b:", a + b)
    print("a - b (양수만):", a - b)
    print("a & b (min):", a & b, "| a | b (max):", a | b)
    print("+c 음수·0 제거:", +Counter(x=2, y=0, z=-1))
    assert a - b == Counter(x=2)

    need = Counter("banana")
    short, enough = Counter("aabnnx"), Counter("aaabnnx")
    print("포함 비교 need <= have:", need <= short, need <= enough)   # 3.10+ 비교 연산
    print("부족한 글자:", need - short)
    assert not need <= short and need <= enough


def anagram_and_top():
    print("애너그램:", Counter("listen") == Counter("silent"))
    votes = ["b", "a", "c", "a", "b", "a"]
    winner, count = Counter(votes).most_common(1)[0]
    print("최다 득표:", winner, count)
    tie = Counter(["x", "y", "y", "x"]).most_common()
    print("동점은 처음 나온 순서:", tie)
    assert tie == [("x", 2), ("y", 2)]


if __name__ == "__main__":
    basics()
    update_subtract()
    arithmetic()
    anagram_and_top()
    print("모든 검증 통과")
