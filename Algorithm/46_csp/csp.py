"""제약 만족 문제(CSP): 백트래킹, 전방 검사, MRV·차수 휴리스틱, AC-3. 지도 색칠, 스도쿠, N-Queen."""
import itertools, random


class CSP:
    """variables: 변수 목록, domains: {변수: 값 목록}, neighbors: {변수: 이웃 변수},
    ok(x, a, y, b): x=a, y=b가 함께 가능하면 True (이항 제약)."""

    def __init__(self, variables, domains, neighbors, ok):
        self.variables, self.domains, self.neighbors, self.ok = variables, domains, neighbors, ok


def solve(csp, forward=False, mrv=False, ac3_first=False, count_all=False):
    """반환: (해 또는 해의 개수, 시도한 할당 수)."""
    domains = {v: list(d) for v, d in csp.domains.items()}
    if ac3_first and not ac3(csp, domains): return (0 if count_all else None), 0
    assign, stats = {}, {"assign": 0}
    found = []

    def select():
        un = [v for v in csp.variables if v not in assign]
        if not mrv: return un[0]
        # MRV: 남은 값이 가장 적은 변수. 동점이면 아직 할당 안 된 이웃이 많은 변수(차수 휴리스틱)
        return min(un, key=lambda v: (len(domains[v]), -sum(1 for u in csp.neighbors[v] if u not in assign)))

    def consistent(v, a):
        return all(csp.ok(v, a, u, assign[u]) for u in csp.neighbors[v] if u in assign)

    def bt():
        if len(assign) == len(csp.variables):
            found.append(dict(assign))
            return not count_all                  # 해 하나면 멈추고, 개수를 셀 때는 계속
        v = select()
        for a in list(domains[v]):
            if not consistent(v, a): continue
            stats["assign"] += 1
            assign[v] = a
            pruned, dead = [], False
            if forward:                           # 전방 검사: 이웃의 도메인에서 a와 충돌하는 값을 지운다
                for u in csp.neighbors[v]:
                    if u in assign: continue
                    for b in list(domains[u]):
                        if not csp.ok(v, a, u, b):
                            domains[u].remove(b); pruned.append((u, b))
                    if not domains[u]: dead = True; break   # 이웃 도메인이 비면 이 값은 실패
            if not dead and bt(): return True
            for u, b in pruned: domains[u].append(b)
            del assign[v]
        return False

    bt()
    if count_all: return len(found), stats["assign"]
    return (found[0] if found else None), stats["assign"]


def ac3(csp, domains):
    """호 일관성: 모든 (x, y)에 대해 x의 각 값이 y에 짝이 되는 값을 하나 이상 갖도록 x의 도메인을 줄인다."""
    from collections import deque
    q = deque((x, y) for x in csp.variables for y in csp.neighbors[x])
    while q:
        x, y = q.popleft()
        removed = False
        for a in list(domains[x]):
            if not any(csp.ok(x, a, y, b) for b in domains[y]):
                domains[x].remove(a); removed = True
        if removed:
            if not domains[x]: return False
            for z in csp.neighbors[x]:
                if z != y: q.append((z, x))
    return True


# ---------- 문제 정의 ----------

def map_coloring(colors=("R", "G", "B")):
    edges = [("WA", "NT"), ("WA", "SA"), ("NT", "SA"), ("NT", "Q"), ("SA", "Q"), ("SA", "NSW"), ("SA", "V"), ("Q", "NSW"), ("NSW", "V")]
    vs = ["WA", "NT", "SA", "Q", "NSW", "V", "T"]
    nb = {v: [] for v in vs}
    for a, b in edges: nb[a].append(b); nb[b].append(a)
    return CSP(vs, {v: list(colors) for v in vs}, nb, lambda x, a, y, b: a != b), edges


def sudoku(grid):
    """grid: 81자 문자열, 0 또는 .은 빈칸."""
    cells = [(r, c) for r in range(9) for c in range(9)]
    nb = {}
    for r, c in cells:
        s = {(r, j) for j in range(9)} | {(i, c) for i in range(9)} | \
            {(3 * (r // 3) + i, 3 * (c // 3) + j) for i in range(3) for j in range(3)}
        s.discard((r, c)); nb[(r, c)] = sorted(s)
    dom = {}
    for (r, c), ch in zip(cells, grid):
        dom[(r, c)] = [int(ch)] if ch not in "0." else list(range(1, 10))
    return CSP(cells, dom, nb, lambda x, a, y, b: a != b)


def queens_csp(n):
    vs = list(range(n))
    nb = {v: [u for u in vs if u != v] for v in vs}
    return CSP(vs, {v: list(range(n)) for v in vs}, nb, lambda x, a, y, b: a != b and abs(a - b) != abs(x - y))


def valid_sudoku(sol):
    g = [[sol[(r, c)] for c in range(9)] for r in range(9)]
    ok = lambda xs: sorted(xs) == list(range(1, 10))
    return all(ok(g[r]) for r in range(9)) and all(ok([g[r][c] for r in range(9)]) for c in range(9)) and \
        all(ok([g[3 * br + i][3 * bc + j] for i in range(3) for j in range(3)]) for br in range(3) for bc in range(3))


if __name__ == "__main__":
    import sys
    slow = "--slow" in sys.argv                    # 스도쿠 순수 백트래킹(수십 초 이상)까지 실행
    csp, edges = map_coloring()
    brute = sum(1 for cs in itertools.product("RGB", repeat=7)
                if all(cs[csp.variables.index(a)] != cs[csp.variables.index(b)] for a, b in edges))
    for fw, mrv in ((False, False), (True, False), (True, True)):
        cnt, _ = solve(csp, forward=fw, mrv=mrv, count_all=True)
        assert cnt == brute
    sol, n_assign = solve(csp, forward=True, mrv=True)
    print(f"호주 지도 3색 칠하기: 해의 개수 {brute} (3^7 완전 탐색과 일치), 첫 해 {sol}")
    csp2, _ = map_coloring(("R", "G"))
    print("2색으로는:", solve(csp2, forward=True, mrv=True)[0], "/ AC-3만으로 불가능 판정:", ac3(csp2, {v: list(d) for v, d in csp2.domains.items()}))

    for n in range(4, 9):
        cnt, _ = solve(queens_csp(n), forward=True, mrv=True, count_all=True)
        assert cnt == {4: 2, 5: 10, 6: 4, 7: 40, 8: 92}[n]
    print("N-Queen CSP 해의 개수 4~8: 16번 글의 값과 일치")
    for n in (8, 16, 25):
        line = []
        for name, fw, mrv in (("백트래킹", False, False), ("전방 검사", True, False), ("전방 검사+MRV", True, True)):
            if n == 25 and not fw:
                line.append(f"{name} (생략)"); continue
            s, a = solve(queens_csp(n), forward=fw, mrv=mrv)
            assert s and all(s[i] != s[j] and abs(s[i] - s[j]) != j - i for i in range(n) for j in range(i + 1, n))
            line.append(f"{name} {a:,}")
        print(f"{n}-Queen 첫 해까지 할당 횟수: " + ", ".join(line))

    puzzles = {
        "쉬움": "530070000600195000098000060800060003400803001700020006060000280000419005000080079",
        "어려움": "000000010400000000020000000000050407008000300001090000300400200050100000000806000",
    }
    for name, p in puzzles.items():
        line = []
        for label, fw, mrv in (("백트래킹", False, False), ("전방 검사", True, False), ("전방 검사+MRV", True, True)):
            if not fw and not slow or name == "어려움" and not mrv:
                line.append(f"{label} (생략)"); continue
            s, a = solve(sudoku(p), forward=fw, mrv=mrv)
            assert s and valid_sudoku(s) and all(ch in "0." or s[(i // 9, i % 9)] == int(ch) for i, ch in enumerate(p))
            line.append(f"{label} {a:,}")
        s, a = solve(sudoku(p), forward=True, mrv=True, ac3_first=True)
        assert valid_sudoku(s)
        line.append(f"AC-3 후 전방 검사+MRV {a:,}")
        print(f"스도쿠({name}) 할당 횟수: " + ", ".join(line))
    s, _ = solve(sudoku(puzzles["쉬움"]), forward=True, mrv=True)
    print("쉬움 퍼즐 해 첫 줄:", [s[(0, c)] for c in range(9)])
