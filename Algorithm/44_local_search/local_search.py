"""지역 탐색: 언덕 오르기(최대 경사, 무작위 재시작), 시뮬레이티드 어닐링, 유전 알고리즘.
문제: N-Queen(충돌 수 최소화), 외판원 문제(경로 길이 최소화)."""
import itertools, math, random


# ---------- N-Queen: 상태 = 열마다 퀸이 있는 행. 비용 = 서로 공격하는 퀸 쌍의 수 ----------

def conflicts(state):
    n, c = len(state), 0
    for i in range(n):
        for j in range(i + 1, n):
            if state[i] == state[j] or abs(state[i] - state[j]) == j - i:
                c += 1
    return c


def hill_climb_queens(n, rng, max_steps=1000):
    """매 단계 이웃(퀸 하나를 같은 열의 다른 행으로) 중 비용이 가장 낮은 것으로 이동. 더 나아지지 않으면 멈춘다."""
    state = [rng.randrange(n) for _ in range(n)]
    cost = conflicts(state)
    for step in range(max_steps):
        if cost == 0: return state, 0, step
        best, best_moves = cost, []
        for col in range(n):
            orig = state[col]
            for row in range(n):
                if row == orig: continue
                state[col] = row
                c = conflicts(state)
                if c < best: best, best_moves = c, [(col, row)]
                elif c == best and c < cost: best_moves.append((col, row))
            state[col] = orig
        if best >= cost: return state, cost, step                 # 지역 최솟값(또는 평지)
        col, row = rng.choice(best_moves)
        state[col] = row; cost = best
    return state, cost, max_steps


def random_restart(n, rng):
    restarts, total_steps = 0, 0
    while True:
        s, c, steps = hill_climb_queens(n, rng)
        total_steps += steps
        if c == 0: return s, restarts, total_steps
        restarts += 1


def anneal_queens(n, rng, t0=2.0, cooling=0.995, max_steps=20000):
    """무작위 이웃 하나를 골라, 더 좋으면 이동하고 나쁘면 확률 exp(-Δ/T)로 이동. T는 점점 낮춘다."""
    state = [rng.randrange(n) for _ in range(n)]
    cost, t = conflicts(state), t0
    for step in range(max_steps):
        if cost == 0: return state, 0, step
        col, row = rng.randrange(n), rng.randrange(n)
        orig = state[col]
        if row == orig: continue
        state[col] = row
        c = conflicts(state)
        delta = c - cost
        if delta <= 0 or rng.random() < math.exp(-delta / t):
            cost = c
        else:
            state[col] = orig
        t = max(t * cooling, 1e-3)
    return state, cost, max_steps


# ---------- 외판원 문제 ----------

def tour_len(tour, d):
    return sum(d[tour[i - 1]][tour[i]] for i in range(len(tour)))


def held_karp(d):
    n = len(d)
    INF = float("inf")
    dp = [[INF] * n for _ in range(1 << n)]
    dp[1][0] = 0
    for mask in range(1 << n):
        if not mask & 1: continue
        for i in range(n):
            if dp[mask][i] == INF or not mask >> i & 1: continue
            for j in range(n):
                if not mask >> j & 1:
                    nm = mask | 1 << j
                    v = dp[mask][i] + d[i][j]
                    if v < dp[nm][j]: dp[nm][j] = v
    return min(dp[(1 << n) - 1][i] + d[i][0] for i in range(n))


def two_opt(tour, d):
    """언덕 오르기: 경로의 한 구간을 뒤집어(간선 두 개 교체) 짧아지면 적용. 더 이상 개선이 없으면 멈춘다."""
    tour = tour[:]
    n = len(tour)
    improved = True
    while improved:
        improved = False
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                a, b, c, e = tour[i - 1], tour[i], tour[j], tour[(j + 1) % n]
                if d[a][c] + d[b][e] < d[a][b] + d[c][e]:
                    tour[i:j + 1] = reversed(tour[i:j + 1]); improved = True
    return tour


def anneal_tsp(d, rng, t0=None, cooling=0.9995, steps=60000):
    n = len(d)
    tour = list(range(n)); rng.shuffle(tour)
    cur = tour_len(tour, d)
    best, best_len = tour[:], cur
    t = t0 if t0 is not None else cur / n
    for _ in range(steps):
        i, j = sorted(rng.sample(range(1, n), 2))   # 0번은 고정: 뒤집는 구간 밖의 양 끝 a, e가 항상 구간 밖에 있게
        a, b, c, e = tour[i - 1], tour[i], tour[j], tour[(j + 1) % n]
        delta = d[a][c] + d[b][e] - d[a][b] - d[c][e]
        if delta <= 0 or rng.random() < math.exp(-delta / t):
            tour[i:j + 1] = reversed(tour[i:j + 1]); cur += delta
            if cur < best_len: best, best_len = tour[:], cur
        t *= cooling
    return best, best_len


def genetic_tsp(d, rng, pop_size=120, generations=400, mutation=0.2, elite=4):
    """개체 = 순열. 토너먼트 선택 → 순서 교차(OX) → 구간 뒤집기 돌연변이. 상위 몇 개는 그대로 남긴다(엘리트)."""
    n = len(d)
    def ox(p1, p2):
        i, j = sorted(rng.sample(range(n), 2))
        child = [None] * n
        child[i:j + 1] = p1[i:j + 1]
        fill = [x for x in p2 if x not in child[i:j + 1]]
        k = 0
        for idx in range(n):
            if child[idx] is None: child[idx] = fill[k]; k += 1
        return child
    pop = [rng.sample(range(n), n) for _ in range(pop_size)]
    for _ in range(generations):
        pop.sort(key=lambda t: tour_len(t, d))
        nxt = [p[:] for p in pop[:elite]]
        while len(nxt) < pop_size:
            a = min(rng.sample(pop, 3), key=lambda t: tour_len(t, d))
            b = min(rng.sample(pop, 3), key=lambda t: tour_len(t, d))
            child = ox(a, b)
            if rng.random() < mutation:
                i, j = sorted(rng.sample(range(n), 2))
                child[i:j + 1] = reversed(child[i:j + 1])
            nxt.append(child)
        pop = nxt
    best = min(pop, key=lambda t: tour_len(t, d))
    return best, tour_len(best, d)


def random_cities(rng, n):
    pts = [(rng.randint(0, 100), rng.randint(0, 100)) for _ in range(n)]
    return [[round(math.dist(p, q)) for q in pts] for p in pts]


if __name__ == "__main__":
    rng = random.Random(44)
    n, runs = 8, 300
    hc = [hill_climb_queens(n, rng) for _ in range(runs)]
    ok = [r for r in hc if r[1] == 0]
    print(f"8-Queen 최대 경사 언덕 오르기 {runs}회: 성공 {len(ok)}회 ({100 * len(ok) / runs:.0f}%), "
          f"성공 시 평균 {sum(r[2] for r in ok) / max(1, len(ok)):.1f}단계, 실패 시 평균 {sum(r[2] for r in hc if r[1]) / max(1, runs - len(ok)):.1f}단계에서 멈춤")
    rr = [random_restart(n, rng) for _ in range(runs)]
    assert all(conflicts(s) == 0 for s, _, _ in rr)
    print(f"무작위 재시작 {runs}회: 모두 성공, 평균 재시작 {sum(r[1] for r in rr) / runs:.1f}번, 평균 총 단계 {sum(r[2] for r in rr) / runs:.1f}")
    sa = [anneal_queens(n, rng) for _ in range(runs)]
    ok_sa = [r for r in sa if r[1] == 0]
    print(f"시뮬레이티드 어닐링 {runs}회: 성공 {len(ok_sa)}회, 성공 시 평균 {sum(r[2] for r in ok_sa) / max(1, len(ok_sa)):.0f}단계")
    for big in (20, 30):
        s, restarts, steps = random_restart(big, rng)
        assert conflicts(s) == 0
        print(f"{big}-Queen 무작위 재시작 언덕 오르기: 재시작 {restarts}번, 총 {steps}단계로 해 발견")

    print()
    results = {"2-opt 언덕 오르기(무작위 시작 1회)": [], "2-opt 무작위 재시작 20회": [], "시뮬레이티드 어닐링": [], "유전 알고리즘": []}
    trials = 10
    for _ in range(trials):
        d = random_cities(rng, 12)
        opt = held_karp(d)
        t = list(range(12)); rng.shuffle(t)
        results["2-opt 언덕 오르기(무작위 시작 1회)"].append(tour_len(two_opt(t, d), d) / opt)
        best = min(tour_len(two_opt(rng.sample(range(12), 12), d), d) for _ in range(20))
        results["2-opt 무작위 재시작 20회"].append(best / opt)
        results["시뮬레이티드 어닐링"].append(anneal_tsp(d, rng)[1] / opt)
        results["유전 알고리즘"].append(genetic_tsp(d, rng)[1] / opt)
    print(f"도시 12개 외판원 문제 {trials}개 (최적값은 Held-Karp DP로 계산), 최적 대비 경로 길이:")
    for k, v in results.items():
        print(f"  {k}: 평균 {sum(v) / trials:.3f}배, 최적 도달 {sum(abs(x - 1) < 1e-9 for x in v)}/{trials}")

    d = random_cities(rng, 60)
    t = list(range(60)); rng.shuffle(t)
    print(f"도시 60개: 무작위 경로 {tour_len(t, d)}, 2-opt {tour_len(two_opt(t, d), d)}, "
          f"어닐링 {anneal_tsp(d, rng, steps=200000, cooling=0.99995)[1]}, 유전 {genetic_tsp(d, rng, generations=600)[1]}")
