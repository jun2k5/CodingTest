"""k-평균 군집화: 로이드 알고리즘, 무작위 초기화 vs k-means++, 엘보 방법. 표준 라이브러리만 사용."""
import math, random


def dist2(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b))


def assign(points, centers):
    return [min(range(len(centers)), key=lambda c: dist2(p, centers[c])) for p in points]


def sse(points, centers, labels):
    """군집 내 제곱합(관성): 각 점과 자기 중심 사이 거리 제곱의 합. k-평균이 줄이려는 값."""
    return sum(dist2(p, centers[l]) for p, l in zip(points, labels))


def init_random(points, k, rng):
    return [list(p) for p in rng.sample(points, k)]


def init_kmeanspp(points, k, rng):
    """첫 중심은 무작위. 다음 중심은 '가장 가까운 기존 중심까지 거리²'에 비례하는 확률로 뽑는다 → 멀리 퍼진 중심."""
    centers = [list(rng.choice(points))]
    d = [dist2(p, centers[0]) for p in points]
    for _ in range(1, k):
        total = sum(d)
        r, acc = rng.uniform(0, total), 0.0
        for i, w in enumerate(d):
            acc += w
            if acc >= r: break
        centers.append(list(points[i]))
        d = [min(old, dist2(p, centers[-1])) for old, p in zip(d, points)]
    return centers


def kmeans(points, k, rng, init="kmeans++", max_iter=100, history=None):
    """로이드: (1) 각 점을 가장 가까운 중심에 배정 (2) 중심을 배정된 점들의 평균으로 이동. 배정이 안 바뀌면 끝."""
    centers = init_kmeanspp(points, k, rng) if init == "kmeans++" else init_random(points, k, rng)
    labels = None
    for it in range(max_iter):
        new = assign(points, centers)
        if history is not None: history.append(sse(points, centers, new))
        if new == labels: break
        labels = new
        for c in range(k):
            members = [p for p, l in zip(points, labels) if l == c]
            if members:                            # 빈 군집이면 중심을 그대로 둔다
                centers[c] = [sum(x) / len(members) for x in zip(*members)]
        if history is not None: history.append(sse(points, centers, labels))
    return centers, labels, it + 1


def make_blobs(rng, centers, n_each, spread):
    pts, truth = [], []
    for ci, (cx, cy) in enumerate(centers):
        for _ in range(n_each):
            pts.append((rng.gauss(cx, spread), rng.gauss(cy, spread))); truth.append(ci)
    return pts, truth


def purity(labels, truth, k):
    """각 군집에서 가장 많은 실제 그룹의 비율 합 / 전체."""
    tot = 0
    for c in range(k):
        members = [t for l, t in zip(labels, truth) if l == c]
        if members: tot += max(members.count(t) for t in set(members))
    return tot / len(truth)


if __name__ == "__main__":
    rng = random.Random(54)

    # 검증 1: SSE는 매 단계(배정, 중심 이동) 감소하거나 같다
    for _ in range(200):
        pts = [(rng.uniform(0, 10), rng.uniform(0, 10)) for _ in range(rng.randint(5, 60))]
        k = rng.randint(1, min(5, len(pts)))
        hist = []
        centers, labels, _ = kmeans(pts, k, rng, init=rng.choice(["random", "kmeans++"]), history=hist)
        assert all(b <= a + 1e-9 for a, b in zip(hist, hist[1:]))
        assert labels == assign(pts, centers)      # 끝난 상태: 모든 점이 가장 가까운 중심에 배정
    print("로이드 알고리즘: 200개 입력에서 SSE가 매 단계 단조 감소, 종료 시 모든 점이 가장 가까운 중심에 배정됨")

    # 검증 2: 아주 작은 입력에서 모든 분할을 시도한 최소 SSE와 비교 (k-평균은 지역 최적만 보장)
    hit = 0
    for _ in range(200):
        pts = [(rng.randint(0, 9), rng.randint(0, 9)) for _ in range(7)]
        k = 2
        best = float("inf")
        for mask in range(1, 2 ** 7 - 1):
            groups = [[p for i, p in enumerate(pts) if (mask >> i & 1) == g] for g in (0, 1)]
            cs = [[sum(x) / len(gp) for x in zip(*gp)] for gp in groups]
            best = min(best, sum(dist2(p, cs[g]) for g, gp in enumerate(groups) for p in gp))
        runs = min(sse(pts, c, l) for c, l, _ in (kmeans(pts, k, rng) for _ in range(10)))
        one = sse(pts, *kmeans(pts, k, rng)[:2])
        assert runs >= best - 1e-9
        hit += abs(one - best) < 1e-9
    print(f"점 7개, k=2 전수 분할(126가지) 최소 SSE와 비교: k-means++ 1회 실행이 전역 최적에 도달 {hit}/200")

    centers_true = [(0, 0), (6, 0), (3, 5), (9, 6), (-3, 6)]
    pts, truth = make_blobs(rng, centers_true, 100, 1.0)
    for init in ("random", "kmeans++"):
        res = [kmeans(pts, 5, rng, init=init) for _ in range(50)]
        s = [sse(pts, c, l) for c, l, _ in res]
        good = sum(abs(v - min(s)) / min(s) < 0.01 for v in s)
        print(f"5개 덩어리 500점, {init:9s} 초기화 50회: SSE 평균 {sum(s) / 50:,.0f}, 최소 {min(s):,.0f}, 최대 {max(s):,.0f}, "
              f"최소의 1% 이내 {good}/50, 평균 반복 {sum(r[2] for r in res) / 50:.1f}")
    c, l, _ = kmeans(pts, 5, rng)
    print(f"k-means++ 결과 순도(실제 덩어리와 일치 비율): {purity(l, truth, 5):.3f}")
    print("찾은 중심:", sorted((round(x, 1), round(y, 1)) for x, y in c))

    print("엘보 방법 (k별 최소 SSE, 각 10회 중 최소):")
    prev = None
    for k in range(1, 9):
        best = min(sse(pts, *kmeans(pts, k, rng)[:2]) for _ in range(10))
        drop = f"  (이전 대비 -{100 * (1 - best / prev):.0f}%)" if prev else ""
        print(f"  k={k}: {best:,.0f}{drop}")
        prev = best
