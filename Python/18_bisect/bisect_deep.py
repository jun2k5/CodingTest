"""18. bisect 심화: left/right 차이, insort, key=(3.10+), 구간 찾기, 개수 세기, 정렬 유지 비용"""
import bisect
import timeit


def left_right():
    a = [10, 20, 20, 20, 30]
    print("bisect_left(20):", bisect.bisect_left(a, 20), "| bisect_right(20):", bisect.bisect_right(a, 20))
    print("없는 값 25:", bisect.bisect_left(a, 25), bisect.bisect_right(a, 25))
    count = bisect.bisect_right(a, 20) - bisect.bisect_left(a, 20)
    print("20의 개수:", count)
    assert count == 3

    def contains(arr, x):
        i = bisect.bisect_left(arr, x)
        return i < len(arr) and arr[i] == x
    print("이진 탐색 존재 확인:", contains(a, 30), contains(a, 25))


def range_count():
    scores = sorted([55, 72, 88, 91, 64, 77, 99, 82])
    lo, hi = 70, 89
    n = bisect.bisect_right(scores, hi) - bisect.bisect_left(scores, lo)
    print(f"{lo}~{hi}점 학생 수:", n, "| 정렬:", scores)
    assert n == 4


def grade_table():
    breakpoints = [60, 70, 80, 90]
    grades = "FDCBA"

    def grade(score):
        return grades[bisect.bisect_right(breakpoints, score)]
    print("등급:", [grade(s) for s in (33, 60, 79, 80, 90, 100)])
    assert [grade(s) for s in (59, 60, 89, 90)] == ["F", "D", "B", "A"]


def insort_keep_sorted():
    a = []
    for x in [5, 1, 4, 1, 3]:
        bisect.insort(a, x)
    print("insort로 정렬 유지:", a)


def key_parameter():
    events = [("09:00", "open"), ("12:30", "lunch"), ("18:00", "close")]
    i = bisect.bisect_left(events, "12:00", key=lambda e: e[0])     # 3.10+
    print("key=로 검색:", i, events[i])
    bisect.insort(events, ("15:00", "meeting"), key=lambda e: e[0])
    print("key=로 삽입:", [e[1] for e in events])
    assert [e[1] for e in events] == ["open", "lunch", "meeting", "close"]


def lis_length(nums):
    """최장 증가 부분 수열 길이 O(n log n): tails[i] = 길이 i+1 수열의 최소 끝값"""
    tails = []
    for x in nums:
        i = bisect.bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)


def insertion_cost():
    t = timeit.timeit("bisect.insort(a, 50_000)", setup="import bisect; a=list(range(100_000))", number=2000)
    print(f"원소 10만 개 리스트에 insort 2000번: {t * 1000:.1f}ms (검색은 O(log n), 삽입 이동은 O(n))")


if __name__ == "__main__":
    left_right()
    range_count()
    grade_table()
    insort_keep_sorted()
    key_parameter()
    print("LIS 길이:", lis_length([10, 9, 2, 5, 3, 7, 101, 18]))
    assert lis_length([10, 9, 2, 5, 3, 7, 101, 18]) == 4
    insertion_cost()
    print("모든 검증 통과")
