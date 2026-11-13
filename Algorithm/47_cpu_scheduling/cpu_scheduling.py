"""CPU 스케줄링: FCFS, SJF, SRT, HRN, 우선순위, 라운드 로빈. 간트 차트와 평균 대기·반환 시간."""
import heapq, itertools, random
from collections import deque


def summarize(procs, finish):
    """procs = [(이름, 도착, 실행 시간)]. 반환 시간 = 종료 - 도착, 대기 시간 = 반환 - 실행."""
    tat = {p: finish[p] - a for p, a, b in procs}
    wait = {p: tat[p] - b for p, a, b in procs}
    n = len(procs)
    return sum(wait.values()) / n, sum(tat.values()) / n, wait


def nonpreemptive(procs, pick):
    """CPU가 비면 도착한 프로세스 중 pick 기준이 가장 작은 것을 끝까지 실행."""
    t, done, gantt, finish = 0, set(), [], {}
    while len(done) < len(procs):
        ready = [p for p in procs if p[1] <= t and p[0] not in done]
        if not ready:
            t = min(p[1] for p in procs if p[0] not in done)
            continue
        name, arr, burst = min(ready, key=lambda p: pick(p, t))
        gantt.append((name, t, t + burst))
        t += burst; finish[name] = t; done.add(name)
    return gantt, finish


def fcfs(procs):
    return nonpreemptive(procs, lambda p, t: (p[1], p[0]))


def sjf(procs):
    return nonpreemptive(procs, lambda p, t: (p[2], p[1], p[0]))


def hrn(procs):
    """응답률 = (대기 시간 + 실행 시간) / 실행 시간. 높은 것 먼저 → 오래 기다린 긴 작업도 결국 실행된다."""
    return nonpreemptive(procs, lambda p, t: (-((t - p[1]) + p[2]) / p[2], p[1], p[0]))


def priority_np(procs, prio):
    return nonpreemptive(procs, lambda p, t: (prio[p[0]], p[1], p[0]))


def srt(procs):
    """SJF의 선점형: 매 시점 남은 시간이 가장 짧은 프로세스를 실행. 새 프로세스가 오면 다시 비교."""
    events = sorted(procs, key=lambda p: p[1])
    remain = {p[0]: p[2] for p in procs}
    t, i, heap, gantt, finish = 0, 0, [], [], {}
    while len(finish) < len(procs):
        while i < len(events) and events[i][1] <= t:
            heapq.heappush(heap, (remain[events[i][0]], events[i][1], events[i][0])); i += 1
        if not heap:
            t = events[i][1]; continue
        r, arr, name = heapq.heappop(heap)
        nxt = events[i][1] if i < len(events) else float("inf")
        run = min(r, nxt - t)                      # 다음 도착 시점까지만 실행하고 다시 고른다
        if gantt and gantt[-1][0] == name and gantt[-1][2] == t:
            gantt[-1] = (name, gantt[-1][1], t + run)
        else:
            gantt.append((name, t, t + run))
        t += run; remain[name] -= run
        if remain[name] == 0: finish[name] = t
        else: heapq.heappush(heap, (remain[name], arr, name))
    return gantt, finish


def round_robin(procs, q):
    """도착 순으로 큐에 넣고 시간 할당량 q만큼씩 돌아가며 실행. 다 못 끝내면 큐 뒤로."""
    events = sorted(procs, key=lambda p: (p[1], p[0]))
    remain = {p[0]: p[2] for p in procs}
    t, i, queue, gantt, finish = 0, 0, deque(), [], {}
    while len(finish) < len(procs):
        while i < len(events) and events[i][1] <= t:
            queue.append(events[i][0]); i += 1
        if not queue:
            t = events[i][1]; continue
        name = queue.popleft()
        run = min(q, remain[name])
        gantt.append((name, t, t + run))
        t += run; remain[name] -= run
        while i < len(events) and events[i][1] <= t:   # 실행 중 도착한 프로세스가 먼저 큐에 들어간다
            queue.append(events[i][0]); i += 1
        if remain[name]: queue.append(name)
        else: finish[name] = t
    return gantt, finish


def gantt_str(g):
    return " | ".join(f"{n} {s}-{e}" for n, s, e in g)


def check_schedule(procs, gantt, finish):
    """검증: 같은 시각에 두 프로세스가 실행되지 않고, 각자 도착 후에만 실행되며, 실행 시간 합이 정확하다."""
    used = {}
    arr = {p: a for p, a, b in procs}
    for n, s, e in gantt:
        assert s >= arr[n] and e > s
        used[n] = used.get(n, 0) + e - s
    assert all(used[p] == b for p, a, b in procs)
    seg = sorted((s, e) for _, s, e in gantt)
    assert all(seg[k][1] <= seg[k + 1][0] for k in range(len(seg) - 1))
    assert all(finish[n] == max(e for m, s, e in gantt if m == n) for n in finish)


if __name__ == "__main__":
    procs = [("P1", 0, 8), ("P2", 1, 4), ("P3", 2, 9), ("P4", 3, 5)]
    print("프로세스 (이름, 도착, 실행):", procs)
    for name, f in (("FCFS", fcfs), ("SJF", sjf), ("SRT", srt), ("HRN", hrn), ("RR(q=4)", lambda p: round_robin(p, 4))):
        g, fin = f(procs)
        check_schedule(procs, g, fin)
        w, tt, _ = summarize(procs, fin)
        print(f"  {name:8s} 평균 대기 {w:5.2f}  평균 반환 {tt:5.2f}  | {gantt_str(g)}")

    # 모두 시각 0에 도착하면 SJF가 비선점 순서 중 평균 대기 시간 최소 (모든 순서와 비교)
    rng = random.Random(47)
    for _ in range(300):
        n = rng.randint(1, 6)
        ps = [(f"P{k}", 0, rng.randint(1, 10)) for k in range(n)]
        best = min(sum(sum(b for _, _, b in order[:k]) for k in range(n)) / n for order in itertools.permutations(ps))
        g, fin = sjf(ps)
        assert abs(summarize(ps, fin)[0] - best) < 1e-9
    print("모두 동시에 도착할 때 SJF 평균 대기 시간 = 모든 실행 순서 중 최솟값 (300개 입력)")

    # 도착 시간이 다르면 SRT가 SJF보다 평균 대기가 같거나 짧다, 모든 스케줄 유효성 검사
    better = 0
    for _ in range(500):
        n = rng.randint(1, 7)
        ps = [(f"P{k}", rng.randint(0, 15), rng.randint(1, 10)) for k in range(n)]
        res = {}
        for name, f in (("FCFS", fcfs), ("SJF", sjf), ("SRT", srt), ("HRN", hrn), ("RR", lambda p: round_robin(p, 3))):
            g, fin = f(ps)
            check_schedule(ps, g, fin)
            res[name] = summarize(ps, fin)[0]
        assert res["SRT"] <= res["SJF"] + 1e-9
        better += res["SRT"] < res["SJF"] - 1e-9
    print(f"무작위 500개: 모든 알고리즘 스케줄 유효(겹침 없음, 도착 후 실행, 실행 시간 정확). SRT ≤ SJF, 그중 {better}개는 SRT가 더 짧음")

    # 라운드 로빈: 할당량에 따른 변화
    ps = [("P1", 0, 24), ("P2", 0, 3), ("P3", 0, 3)]
    for q in (1, 4, 10, 30):
        g, fin = round_robin(ps, q)
        w, tt, _ = summarize(ps, fin)
        print(f"RR q={q:2d}: 평균 대기 {w:5.2f}, 평균 반환 {tt:5.2f}, 문맥 교환 {len(g) - 1}번")
    g, fin = fcfs(ps)
    print(f"FCFS(긴 작업 먼저 도착, 호위 효과): 평균 대기 {summarize(ps, fin)[0]:.2f}")

    # HRN: 오래 기다린 긴 작업이 짧은 작업보다 먼저 선택되는 예
    ps = [("A", 0, 3), ("B", 1, 6), ("C", 4, 4), ("D", 6, 5), ("E", 8, 2)]
    for name, f in (("SJF", sjf), ("HRN", hrn)):
        g, fin = f(ps)
        print(f"{name}: {gantt_str(g)}  평균 대기 {summarize(ps, fin)[0]:.2f}")
