"""배열 기법: 누적 합(1차원·2차원), 차분 배열, 투 포인터, 슬라이딩 윈도우, 좌표 압축."""
import random
from collections import deque


def prefix_sums(a):
    p = [0]
    for x in a: p.append(p[-1] + x)
    return p                                       # 구간 [l, r] 합 = p[r + 1] - p[l]


def prefix_2d(grid):
    n, m = len(grid), len(grid[0])
    p = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n):
        for j in range(m):
            p[i + 1][j + 1] = grid[i][j] + p[i][j + 1] + p[i + 1][j] - p[i][j]
    return p                                       # (r1,c1)~(r2,c2) = p[r2+1][c2+1] - p[r1][c2+1] - p[r2+1][c1] + p[r1][c1]


def apply_range_adds(n, ops):
    """차분 배열: 구간 [l, r]에 v를 더하는 연산 여러 개를 O(n + 연산 수)에."""
    diff = [0] * (n + 1)
    for l, r, v in ops:
        diff[l] += v; diff[r + 1] -= v
    out, cur = [], 0
    for i in range(n):
        cur += diff[i]; out.append(cur)
    return out


def count_subarrays_with_sum(a, target):
    """양수 배열에서 합이 target인 연속 구간 수. 투 포인터."""
    cnt, s, l = 0, 0, 0
    for r, x in enumerate(a):
        s += x
        while s > target and l <= r:
            s -= a[l]; l += 1
        if s == target:
            cnt += 1
    return cnt


def two_sum_sorted(a, target):
    """정렬된 배열에서 합이 target인 쌍 수(서로 다른 인덱스). 양 끝에서 좁혀 온다."""
    a = sorted(a)
    i, j, cnt = 0, len(a) - 1, 0
    while i < j:
        s = a[i] + a[j]
        if s == target:
            if a[i] == a[j]:
                k = j - i + 1; cnt += k * (k - 1) // 2; break
            li = ri = 1
            while i + li < j and a[i + li] == a[i]: li += 1
            while j - ri > i and a[j - ri] == a[j]: ri += 1
            cnt += li * ri; i += li; j -= ri
        elif s < target:
            i += 1
        else:
            j -= 1
    return cnt


def max_window_sum(a, k):
    s = best = sum(a[:k])
    for i in range(k, len(a)):
        s += a[i] - a[i - k]                       # 들어온 값 더하고 나간 값 빼기
        best = max(best, s)
    return best


def sliding_max(a, k):
    """길이 k 창마다 최댓값. 덱에 '앞으로 최댓값이 될 수 있는' 인덱스만 감소 순으로 유지. O(n)."""
    dq, out = deque(), []
    for i, x in enumerate(a):
        while dq and a[dq[-1]] <= x: dq.pop()
        dq.append(i)
        if dq[0] <= i - k: dq.popleft()
        if i >= k - 1: out.append(a[dq[0]])
    return out


def compress(a):
    """값을 순위(0부터)로 바꾼다."""
    rank = {v: i for i, v in enumerate(sorted(set(a)))}
    return [rank[v] for v in a]


if __name__ == "__main__":
    rng = random.Random(89)
    for _ in range(300):
        a = [rng.randint(-10, 10) for _ in range(rng.randint(1, 30))]
        p = prefix_sums(a)
        l = rng.randrange(len(a)); r = rng.randrange(l, len(a))
        assert p[r + 1] - p[l] == sum(a[l:r + 1])
        g = [[rng.randint(-5, 5) for _ in range(rng.randint(1, 6))] for _ in range(rng.randint(1, 6))]
        g = [row[:len(g[0])] + [0] * (len(g[0]) - len(row)) for row in g]
        P = prefix_2d(g)
        r1 = rng.randrange(len(g)); r2 = rng.randrange(r1, len(g)); c1 = rng.randrange(len(g[0])); c2 = rng.randrange(c1, len(g[0]))
        assert P[r2 + 1][c2 + 1] - P[r1][c2 + 1] - P[r2 + 1][c1] + P[r1][c1] == sum(g[i][j] for i in range(r1, r2 + 1) for j in range(c1, c2 + 1))
        n = len(a)
        ops = [(lambda l: (l, rng.randrange(l, n), rng.randint(-3, 3)))(rng.randrange(n)) for _ in range(rng.randint(0, 10))]
        ref = [0] * n
        for l2, r2_, v in ops:
            for i in range(l2, r2_ + 1): ref[i] += v
        assert apply_range_adds(n, ops) == ref
        pos = [rng.randint(1, 5) for _ in range(rng.randint(1, 25))]
        t = rng.randint(1, 15)
        assert count_subarrays_with_sum(pos, t) == sum(1 for i in range(len(pos)) for j in range(i, len(pos)) if sum(pos[i:j + 1]) == t)
        assert two_sum_sorted(a, 0) == sum(1 for i in range(n) for j in range(i + 1, n) if a[i] + a[j] == 0)
        k = rng.randint(1, n)
        assert max_window_sum(a, k) == max(sum(a[i:i + k]) for i in range(n - k + 1))
        assert sliding_max(a, k) == [max(a[i:i + k]) for i in range(n - k + 1)]
        c = compress(a)
        assert all((a[i] < a[j]) == (c[i] < c[j]) for i in range(n) for j in range(n))
    print("누적 합(1·2차원), 차분 배열, 투 포인터 2종, 슬라이딩 윈도우 2종, 좌표 압축: 300개 입력에서 단순 계산과 일치")
    print("sliding_max([1,3,-1,-3,5,3,6,7], 3) ->", sliding_max([1, 3, -1, -3, 5, 3, 6, 7], 3))
    print("compress([100, -5, 100, 42]) ->", compress([100, -5, 100, 42]))
    print("차분 배열 n=5, [0,2]+3, [1,4]+2 ->", apply_range_adds(5, [(0, 2, 3), (1, 4, 2)]))
