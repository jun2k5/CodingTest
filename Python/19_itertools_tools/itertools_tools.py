"""19. itertools ① 이터레이터 도구: 무한, 자르기·필터, 누적, 그룹, 묶기"""
import itertools as it
import operator


def infinite():
    print("count(10, 5):", list(it.islice(it.count(10, 5), 4)))
    print("cycle:", list(it.islice(it.cycle("AB"), 5)))
    print("repeat:", list(it.repeat("x", 3)), "| map 상수 인자:", list(map(pow, range(4), it.repeat(2))))
    ids = dict(zip(["kim", "lee", "park"], it.count(1)))
    print("번호 매기기:", ids)


def slicing_filtering():
    data = [1, 4, 6, 2, 8, 3, 9]
    print("islice(1, 6, 2):", list(it.islice(data, 1, 6, 2)))
    print("takewhile(<7):", list(it.takewhile(lambda x: x < 7, data)))
    print("dropwhile(<7):", list(it.dropwhile(lambda x: x < 7, data)))
    print("filterfalse(짝수):", list(it.filterfalse(lambda x: x % 2 == 0, data)))
    print("compress:", list(it.compress("ABCDE", [1, 0, 1, 0, 1])))

    with open(__file__, encoding="utf-8") as f:
        header = list(it.islice(f, 1))           # 파일도 이터레이터: 첫 줄만
    print("파일 첫 줄 시작:", header[0][:12])


def accumulate_demo():
    sales = [3, 1, 4, 1, 5]
    print("누적 합:", list(it.accumulate(sales)))
    print("누적 최댓값:", list(it.accumulate(sales, max)))
    print("누적 곱, 초기값:", list(it.accumulate(sales, operator.mul, initial=1)))
    balance = list(it.accumulate([100, -30, -50, 20], initial=0))
    print("잔고 흐름:", balance)
    assert list(it.accumulate(sales)) == [3, 4, 8, 9, 14]


def chaining():
    print("chain:", list(it.chain([1, 2], "ab", (3,))))
    nested = [[1, 2], [3], [4, 5]]
    print("chain.from_iterable(평탄화):", list(it.chain.from_iterable(nested)))


def grouping():
    logs = ["E:disk", "E:net", "W:cpu", "E:mem", "E:mem"]
    print("groupby(연속 같은 키만):", [(k, len(list(g))) for k, g in it.groupby(logs, key=lambda s: s[0])])
    by_level = {k: [s[2:] for s in g] for k, g in it.groupby(sorted(logs), key=lambda s: s[0])}
    print("정렬 후 groupby:", by_level)
    print("연속 압축(RLE):", "".join(f"{k}{len(list(g))}" for k, g in it.groupby("aaabccdddd")))


def pairing_batching():
    temps = [20, 22, 21, 25]
    print("pairwise 변화량:", [b - a for a, b in it.pairwise(temps)])      # 3.10+
    print("batched(3):", list(it.batched(range(8), 3)))                    # 3.12+
    try:
        list(it.batched(range(8), 3, strict=True))                         # 3.13+
    except ValueError as e:
        print("batched strict:", e)
    print("zip_longest:", list(it.zip_longest("ab", [1, 2, 3], fillvalue="-")))
    print("starmap:", list(it.starmap(pow, [(2, 3), (3, 2)])))


def tee_and_exhaustion():
    src = iter(range(5))
    a, b = it.tee(src, 2)
    print("tee로 복제:", list(a), list(b))
    gen = (x for x in range(3))
    list(it.islice(gen, 2))
    print("islice도 원본을 소비:", list(gen))


if __name__ == "__main__":
    infinite()
    slicing_filtering()
    accumulate_demo()
    chaining()
    grouping()
    pairing_batching()
    tee_and_exhaustion()
    print("모든 검증 통과")
