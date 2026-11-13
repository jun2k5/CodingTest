"""교착 상태 회피(은행원 알고리즘)와 디스크 스케줄링(FCFS, SSTF, SCAN, C-SCAN, LOOK, C-LOOK)."""
import itertools, random


# ---------- 은행원 알고리즘 ----------

def is_safe(available, max_need, alloc):
    """안전 순서가 있으면 그 순서를, 없으면 None. need = max - alloc.
    지금 가용 자원으로 need를 채울 수 있는 프로세스를 끝내고, 그 프로세스가 가진 자원을 돌려받는 것을 반복."""
    n, m = len(alloc), len(available)
    need = [[max_need[i][j] - alloc[i][j] for j in range(m)] for i in range(n)]
    work, finished, order = available[:], [False] * n, []
    progress = True
    while progress:
        progress = False
        for i in range(n):
            if not finished[i] and all(need[i][j] <= work[j] for j in range(m)):
                for j in range(m): work[j] += alloc[i][j]
                finished[i] = True; order.append(i); progress = True
    return order if all(finished) else None


def request(available, max_need, alloc, i, req):
    """프로세스 i의 요청을 가상으로 허락해 보고, 그 뒤에도 안전하면 허락."""
    m = len(available)
    need_i = [max_need[i][j] - alloc[i][j] for j in range(m)]
    if any(req[j] > need_i[j] for j in range(m)): return "error: 최대 요구량 초과", None
    if any(req[j] > available[j] for j in range(m)): return "wait: 가용 자원 부족", None
    av = [available[j] - req[j] for j in range(m)]
    al = [row[:] for row in alloc]
    for j in range(m): al[i][j] += req[j]
    order = is_safe(av, max_need, al)
    return ("grant" if order else "wait: 허락하면 불안전 상태"), order


def safe_brute(available, max_need, alloc):
    n, m = len(alloc), len(available)
    for perm in itertools.permutations(range(n)):
        work, ok = available[:], True
        for i in perm:
            if any(max_need[i][j] - alloc[i][j] > work[j] for j in range(m)): ok = False; break
            for j in range(m): work[j] += alloc[i][j]
        if ok: return True
    return False


# ---------- 디스크 스케줄링 ----------

def fcfs_disk(head, reqs, **_):
    path = [head] + reqs
    return path


def sstf(head, reqs, **_):
    """현재 위치에서 가장 가까운 요청부터. 같으면 번호가 작은 쪽."""
    left, path, cur = list(reqs), [head], head
    while left:
        nxt = min(left, key=lambda r: (abs(r - cur), r))
        left.remove(nxt); path.append(nxt); cur = nxt
    return path


def scan(head, reqs, direction="down", max_cyl=199, **_):
    """엘리베이터: 한 방향 끝(실린더 0 또는 max)까지 가며 처리하고 되돌아온다."""
    lo = sorted(r for r in reqs if r < head); hi = sorted(r for r in reqs if r >= head)
    if direction == "down":
        return [head] + lo[::-1] + ([0] if hi else []) + hi
    return [head] + hi + ([max_cyl] if lo else []) + lo[::-1]


def c_scan(head, reqs, direction="up", max_cyl=199, **_):
    """한 방향으로만 처리. 끝에 닿으면 반대쪽 끝으로 바로 돌아가(이동 거리에 포함) 같은 방향으로 다시 처리."""
    lo = sorted(r for r in reqs if r < head); hi = sorted(r for r in reqs if r >= head)
    if direction == "up":
        return [head] + hi + ([max_cyl, 0] if lo else []) + lo
    return [head] + lo[::-1] + ([0, max_cyl] if hi else []) + hi[::-1]


def look(head, reqs, direction="down", **_):
    """SCAN과 같지만 끝까지 가지 않고 마지막 요청에서 방향을 바꾼다."""
    lo = sorted(r for r in reqs if r < head); hi = sorted(r for r in reqs if r >= head)
    return [head] + (lo[::-1] + hi if direction == "down" else hi + lo[::-1])


def c_look(head, reqs, direction="up", **_):
    lo = sorted(r for r in reqs if r < head); hi = sorted(r for r in reqs if r >= head)
    return [head] + (hi + lo if direction == "up" else lo[::-1] + hi[::-1])


def movement(path):
    return sum(abs(a - b) for a, b in zip(path, path[1:]))


if __name__ == "__main__":
    # 교과서 예제: 프로세스 5개, 자원 A(10) B(5) C(7)
    available = [3, 3, 2]
    max_need = [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]]
    alloc = [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]]
    print("안전 순서:", ["P%d" % i for i in is_safe(available, max_need, alloc)])
    for i, req in ((1, [1, 0, 2]), (4, [3, 3, 0]), (0, [0, 2, 0])):
        res, order = request(available, max_need, alloc, i, req)
        print(f"P{i}가 {req} 요청 -> {res}" + (f", 안전 순서 {['P%d' % k for k in order]}" if order else ""))

    rng = random.Random(49)
    unsafe = 0
    for _ in range(2000):
        n, m = rng.randint(1, 5), rng.randint(1, 3)
        max_need = [[rng.randint(0, 6) for _ in range(m)] for _ in range(n)]
        alloc = [[rng.randint(0, x) for x in row] for row in max_need]
        available = [rng.randint(0, 4) for _ in range(m)]
        order = is_safe(available, max_need, alloc)
        assert (order is not None) == safe_brute(available, max_need, alloc)
        unsafe += order is None
    print(f"은행원 알고리즘 안전성 판정: 2000개 상태(불안전 {unsafe}개)에서 모든 실행 순서 완전 탐색과 일치")

    print()
    head, reqs = 53, [98, 183, 37, 122, 14, 124, 65, 67]
    print(f"디스크 요청 {reqs}, 헤드 {head}, 실린더 0~199")
    for name, f, kw in (("FCFS", fcfs_disk, {}), ("SSTF", sstf, {}), ("SCAN(0 쪽으로)", scan, {"direction": "down"}),
                        ("C-SCAN(199 쪽으로)", c_scan, {"direction": "up"}), ("LOOK(0 쪽으로)", look, {"direction": "down"}),
                        ("C-LOOK(199 쪽으로)", c_look, {"direction": "up"})):
        p = f(head, reqs, **kw)
        assert sorted(x for x in p[1:] if x in reqs) == sorted(reqs)
        print(f"  {name:17s} 총 이동 {movement(p):4d}  경로 {p}")

    # SSTF는 매번 가까운 것을 고를 뿐 전체 최소는 아니다: 모든 순서 중 최솟값과 비교
    worse = 0
    for _ in range(300):
        h = rng.randint(0, 199)
        rq = rng.sample(range(200), rng.randint(1, 7))
        best = min(movement([h] + list(p)) for p in itertools.permutations(rq))
        s = movement(sstf(h, rq))
        assert s >= best
        worse += s > best
        assert movement(look(h, rq, direction="down")) >= best and movement(look(h, rq, direction="up")) >= best
    print(f"무작위 300개: SSTF가 최적 순서보다 이동이 긴 경우 {worse}개 (그리디라 최적 보장 없음)")
    print("  (요청이 한 직선 위에 있으므로 최적은 '한쪽 끝 요청까지 갔다가 반대쪽 끝 요청까지' 가는 두 LOOK 중 짧은 쪽이다)")
    for _ in range(300):
        h = rng.randint(0, 199)
        rq = rng.sample(range(200), rng.randint(1, 7))
        best = min(movement([h] + list(p)) for p in itertools.permutations(rq))
        assert best == min(movement(look(h, rq, direction="down")), movement(look(h, rq, direction="up")))
    print("  확인: 300개 입력에서 min(LOOK 아래 먼저, LOOK 위 먼저) = 모든 순서 중 최소 이동")

    # 기아: SSTF에서 가운데 근처 요청이 계속 들어오면 먼 요청이 계속 밀린다
    cur, served_far, t = 100, None, 0
    pending = [5]
    for step in range(30):
        pending.append(100 + rng.randint(-10, 10))   # 헤드 근처 새 요청이 계속 도착
        nxt = min(pending, key=lambda r: (abs(r - cur), r))
        pending.remove(nxt); cur = nxt
        if nxt == 5: served_far = step; break
    print("SSTF 기아 예: 헤드 근처에 새 요청이 계속 들어오는 동안 실린더 5 요청 처리 여부:",
          "처리됨" if served_far is not None else "30번 처리하는 동안 한 번도 처리 안 됨")
