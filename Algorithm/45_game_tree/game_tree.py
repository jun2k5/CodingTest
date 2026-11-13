"""게임 트리 탐색: 미니맥스, 알파-베타 가지치기, 수 정렬, 틱택토 완전 탐색."""
import random

LINES = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]


def winner(b):
    for a, c, d in LINES:
        if b[a] != "." and b[a] == b[c] == b[d]:
            return b[a]
    return None


def moves(b):
    return [i for i, x in enumerate(b) if x == "."]


class Stats:
    nodes = 0


def minimax(b, player, st):
    """X가 최대화(+1), O가 최소화(-1), 무승부 0. 반환: (값, 최선의 수)."""
    st.nodes += 1
    w = winner(b)
    if w: return (1 if w == "X" else -1), None
    ms = moves(b)
    if not ms: return 0, None
    best = (-2, None) if player == "X" else (2, None)
    for m in ms:
        b[m] = player
        v, _ = minimax(b, "O" if player == "X" else "X", st)
        b[m] = "."
        if (player == "X" and v > best[0]) or (player == "O" and v < best[0]):
            best = (v, m)
    return best


def alphabeta(b, player, alpha, beta, st, order=False):
    """alpha = 최대화 쪽이 이미 확보한 값, beta = 최소화 쪽이 이미 확보한 값.
    alpha >= beta가 되면 상대가 이 가지로 오지 않으므로 나머지 수를 보지 않는다."""
    st.nodes += 1
    w = winner(b)
    if w: return (1 if w == "X" else -1), None
    ms = moves(b)
    if not ms: return 0, None
    if order:                                    # 가운데 → 모서리 → 변 순서로 먼저 본다
        pri = {4: 0, 0: 1, 2: 1, 6: 1, 8: 1}
        ms.sort(key=lambda m: pri.get(m, 2))
    best_move = None
    if player == "X":
        v = -2
        for m in ms:
            b[m] = "X"
            r, _ = alphabeta(b, "O", alpha, beta, st, order)
            b[m] = "."
            if r > v: v, best_move = r, m
            alpha = max(alpha, v)
            if alpha >= beta: break                # 베타 컷
        return v, best_move
    v = 2
    for m in ms:
        b[m] = "O"
        r, _ = alphabeta(b, "X", alpha, beta, st, order)
        b[m] = "."
        if r < v: v, best_move = r, m
        beta = min(beta, v)
        if alpha >= beta: break                    # 알파 컷
    return v, best_move


# ---------- 무작위 게임 트리: 깊이 d, 가지 b, 잎에 정수 값 ----------

def make_tree(rng, depth, branch):
    if depth == 0: return rng.randint(-50, 50)
    return [make_tree(rng, depth - 1, branch) for _ in range(branch)]


def tree_minimax(node, maximize, st):
    st.nodes += 1
    if isinstance(node, int): return node
    vals = [tree_minimax(c, not maximize, st) for c in node]
    return max(vals) if maximize else min(vals)


def tree_alphabeta(node, maximize, alpha, beta, st):
    st.nodes += 1
    if isinstance(node, int): return node
    if maximize:
        v = float("-inf")
        for c in node:
            v = max(v, tree_alphabeta(c, False, alpha, beta, st))
            alpha = max(alpha, v)
            if alpha >= beta: break
        return v
    v = float("inf")
    for c in node:
        v = min(v, tree_alphabeta(c, True, alpha, beta, st))
        beta = min(beta, v)
        if alpha >= beta: break
    return v


def sort_tree(node, maximize):
    """검증·비교용: 모든 노드의 자식을 그 노드의 실제 값 기준 '최선 먼저'로 정렬 (완벽한 수 정렬)."""
    if isinstance(node, int): return node, node
    kids = [sort_tree(c, not maximize) for c in node]
    kids.sort(key=lambda kv: kv[1], reverse=maximize)
    return [k for k, _ in kids], kids[0][1]


if __name__ == "__main__":
    b = list(".........")
    s1, s2, s3 = Stats(), Stats(), Stats()
    v1, m1 = minimax(b, "X", s1)
    v2, m2 = alphabeta(b, "X", -2, 2, s2)
    v3, m3 = alphabeta(b, "X", -2, 2, s3, order=True)
    assert v1 == v2 == v3 == 0
    print(f"틱택토 빈 판의 값: {v1} (양쪽이 최선을 다하면 무승부)")
    print(f"방문 노드: 미니맥스 {s1.nodes:,}개, 알파-베타 {s2.nodes:,}개, 알파-베타 + 수 정렬 {s3.nodes:,}개")

    # 모든 도달 가능한 국면에서 미니맥스 값 = 알파-베타 값
    seen, cnt = set(), 0
    def walk(bd, p):
        global cnt
        key = "".join(bd)
        if key in seen: return
        seen.add(key)
        a, _ = minimax(bd, p, Stats()) if len(moves(bd)) <= 6 else (None, None)
        if a is not None:
            c, _ = alphabeta(bd, p, -2, 2, Stats())
            assert a == c
            cnt += 1
        if winner(bd) or not moves(bd): return
        for m in moves(bd):
            bd[m] = p; walk(bd, "O" if p == "X" else "X"); bd[m] = "."
    walk(list("........."), "X")
    print(f"틱택토 도달 가능한 국면 {len(seen):,}개 중 빈칸 6개 이하 {cnt:,}개에서 미니맥스와 알파-베타 값 일치")

    bd = list("X.O.X..O.")                         # X 차례: 8번에 두면 대각선 완성
    print("국면 X.O/.X./.O. 에서 X의 최선의 수:", alphabeta(bd, "X", -2, 2, Stats())[1])

    rng = random.Random(45)
    for _ in range(300):
        t = make_tree(rng, rng.randint(1, 6), rng.randint(2, 4))
        assert tree_minimax(t, True, Stats()) == tree_alphabeta(t, True, float("-inf"), float("inf"), Stats())
    print("무작위 게임 트리 300개에서 미니맥스와 알파-베타 루트 값 일치")

    for depth, branch in ((6, 5), (8, 4), (8, 6)):
        t = make_tree(rng, depth, branch)
        a, b_, c = Stats(), Stats(), Stats()
        tree_minimax(t, True, a)
        tree_alphabeta(t, True, float("-inf"), float("inf"), b_)
        ordered, _ = sort_tree(t, True)
        tree_alphabeta(ordered, True, float("-inf"), float("inf"), c)
        leaves = branch ** depth
        best_case = branch ** ((depth + 1) // 2) + branch ** (depth // 2) - 1
        print(f"깊이 {depth}, 가지 {branch} (잎 {leaves:,}개): 방문 노드 미니맥스 {a.nodes:,}, 알파-베타(무작위 순서) {b_.nodes:,}, "
              f"알파-베타(완벽한 정렬) {c.nodes:,} / 최선 정렬 시 평가하는 잎 수 이론값 {best_case:,}")
