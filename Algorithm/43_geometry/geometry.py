"""계산 기하: CCW, 선분 교차, 다각형 넓이(신발끈), 점의 다각형 내부 판정, 볼록 껍질(모노톤 체인), 스위핑."""
import itertools, random
from fractions import Fraction


def ccw(a, b, c):
    """(b - a) × (c - a)의 부호. 양수: 반시계(왼쪽으로 꺾임), 음수: 시계, 0: 한 직선 위."""
    v = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    return (v > 0) - (v < 0)


def segments_intersect(p1, p2, p3, p4):
    """두 선분이 한 점이라도 공유하면 True. 끝점이 닿는 경우, 한 직선 위에서 겹치는 경우 포함."""
    d1, d2 = ccw(p1, p2, p3) * ccw(p1, p2, p4), ccw(p3, p4, p1) * ccw(p3, p4, p2)
    if d1 == 0 and d2 == 0:                       # 네 점이 한 직선 위: 구간이 겹치는지
        a, b = sorted([p1, p2]); c, d = sorted([p3, p4])
        return not (b < c or d < a)
    return d1 <= 0 and d2 <= 0


def intersect_exact(p1, p2, p3, p4):
    """검증용: p1 + t(p2-p1) = p3 + s(p4-p3)를 분수로 풀어 0 <= t, s <= 1인지 확인."""
    F = Fraction
    dx1, dy1 = p2[0] - p1[0], p2[1] - p1[1]
    dx2, dy2 = p4[0] - p3[0], p4[1] - p3[1]
    den = dx1 * dy2 - dy1 * dx2
    if den != 0:
        t = F((p3[0] - p1[0]) * dy2 - (p3[1] - p1[1]) * dx2, den)
        s = F((p3[0] - p1[0]) * dy1 - (p3[1] - p1[1]) * dx1, den)
        return 0 <= t <= 1 and 0 <= s <= 1
    # 평행(또는 점 선분): 같은 직선 위인지, 그렇다면 매개변수 구간이 겹치는지
    if p1 == p2 and p3 == p4: return p1 == p3
    if p1 == p2: p1, p2, p3, p4 = p3, p4, p1, p2   # 길이 있는 선분을 기준으로
    dx1, dy1 = p2[0] - p1[0], p2[1] - p1[1]
    for q in (p3, p4):
        if (q[0] - p1[0]) * dy1 - (q[1] - p1[1]) * dx1 != 0: return False
    proj = lambda p: F((p[0] - p1[0]) * dx1 + (p[1] - p1[1]) * dy1, dx1 * dx1 + dy1 * dy1)
    lo, hi = sorted([proj(p3), proj(p4)])
    return not (hi < 0 or lo > 1)


def polygon_area2(poly):
    """신발끈 공식. 넓이의 2배(정수)를 돌려준다. 반시계 순서면 양수."""
    return sum(poly[i - 1][0] * poly[i][1] - poly[i][0] * poly[i - 1][1] for i in range(len(poly)))


def point_in_polygon(pt, poly):
    """반직선 교차 횟수(홀수 = 내부). 경계 위면 'boundary'."""
    x, y = pt
    inside = False
    for i in range(len(poly)):
        a, b = poly[i - 1], poly[i]
        if ccw(a, b, pt) == 0 and min(a[0], b[0]) <= x <= max(a[0], b[0]) and min(a[1], b[1]) <= y <= max(a[1], b[1]):
            return "boundary"
        if (a[1] > y) != (b[1] > y):              # 변이 수평선 y를 가로지른다
            # 교점 x좌표 > x 이면 오른쪽으로 쏜 반직선과 만난다 (나눗셈 없이 비교)
            lhs = (x - a[0]) * (b[1] - a[1])
            rhs = (b[0] - a[0]) * (y - a[1])
            if (lhs < rhs) == (b[1] > a[1]): inside = not inside
    return "inside" if inside else "outside"


def convex_hull(points):
    """앤드루의 모노톤 체인: x(같으면 y)로 정렬 후 아래 껍질·위 껍질을 스택으로. 반시계 순서, 한 직선 위 점은 제외."""
    pts = sorted(set(points))
    if len(pts) <= 2: return pts
    def half(seq):
        h = []
        for p in seq:
            while len(h) >= 2 and ccw(h[-2], h[-1], p) <= 0:
                h.pop()
            h.append(p)
        return h
    lower, upper = half(pts), half(reversed(pts))
    return lower[:-1] + upper[:-1]


def hull_brute(points):
    """검증용: 점 p가 껍질의 꼭짓점 ⇔ p가 다른 점들의 볼록 결합이 아님. 모든 순서쌍 (a, b)에 대해
    나머지 점이 모두 한쪽에 있으면 a-b는 껍질의 변이다."""
    pts = sorted(set(points))
    if len(pts) <= 2: return set(pts)
    verts = set()
    for a, b in itertools.permutations(pts, 2):
        if all(ccw(a, b, c) > 0 or (ccw(a, b, c) == 0 and min(a, b) <= c <= max(a, b)) for c in pts if c not in (a, b)):
            verts |= {a, b}
    return verts


def union_length(segments):
    """스위핑: 구간을 시작점 순으로 훑으며 겹치는 것은 합친다. 백준 2170 선 긋기."""
    total, cur_s, cur_e = 0, None, None
    for s, e in sorted(segments):
        if cur_e is None or s > cur_e:
            if cur_e is not None: total += cur_e - cur_s
            cur_s, cur_e = s, e
        else:
            cur_e = max(cur_e, e)
    if cur_e is not None: total += cur_e - cur_s
    return total


if __name__ == "__main__":
    rng = random.Random(43)
    for _ in range(20000):
        pts = [(rng.randint(-4, 4), rng.randint(-4, 4)) for _ in range(4)]
        assert segments_intersect(*pts) == intersect_exact(*pts), pts
    print("선분 교차: 20000개(끝점 접촉·평행·겹침·점 선분 포함)에서 분수로 푼 교점 판정과 일치")

    for _ in range(500):
        pts = [(rng.randint(-10, 10), rng.randint(-10, 10)) for _ in range(rng.randint(1, 25))]
        h = convex_hull(pts)
        assert set(h) == hull_brute(pts), (pts, h)
        if len(h) >= 3:
            assert all(ccw(h[i - 2], h[i - 1], h[i]) > 0 for i in range(len(h)))
    print("볼록 껍질: 500개 점 집합에서 '모든 점이 한쪽에 있는 변' 완전 탐색과 꼭짓점 일치, 반시계 순서 확인")

    square = [(0, 0), (4, 0), (4, 4), (0, 4)]
    print("정사각형 넓이(2배):", polygon_area2(square), " 시계 방향이면:", polygon_area2(square[::-1]))
    poly = [(0, 0), (6, 0), (6, 6), (3, 2), (0, 6)]          # 오목 다각형
    print("오목 다각형 넓이:", polygon_area2(poly) / 2)
    for p in [(1, 1), (3, 4), (3, 2), (6, 3), (7, 1)]:
        print(f"  점 {p}: {point_in_polygon(p, poly)}")
    # 내부 판정 검증: 볼록 다각형은 모든 변에서 왼쪽에 있으면 내부
    for _ in range(300):
        h = convex_hull([(rng.randint(-10, 10), rng.randint(-10, 10)) for _ in range(15)])
        if len(h) < 3: continue
        for _ in range(20):
            p = (rng.randint(-11, 11), rng.randint(-11, 11))
            s = [ccw(h[i - 1], h[i], p) for i in range(len(h))]
            exp = "inside" if all(x > 0 for x in s) else ("outside" if any(x < 0 for x in s) else "boundary")
            assert point_in_polygon(p, h) == exp
    print("점의 다각형 내부 판정: 볼록 다각형 6000개 질의에서 '모든 변의 왼쪽' 판정과 일치")

    pts = [(0, 0), (2, 1), (4, 0), (3, 2), (4, 4), (2, 3), (0, 4), (1, 2), (2, 2)]
    print("볼록 껍질 예제:", convex_hull(pts))

    for _ in range(500):
        segs = [(a, a + rng.randint(0, 10)) for a in (rng.randint(-20, 20) for _ in range(rng.randint(0, 10)))]
        covered = set()
        for s, e in segs: covered |= set(range(s, e))
        assert union_length(segs) == len(covered)
    print("선분 합집합 길이(스위핑): 500개 입력에서 단위 칸 직접 칠하기와 일치")
    print("백준 2170 예제:", union_length([(1, 3), (2, 5), (3, 5), (6, 7)]))
