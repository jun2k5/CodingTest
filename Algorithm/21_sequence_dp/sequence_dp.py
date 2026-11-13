"""수열 DP: LIS(O(n^2), O(n log n) + 복원), LCS(+ 복원), 편집 거리."""
import bisect, itertools, random


def lis_n2(a):
    """dp[i] = a[i]로 끝나는 가장 긴 증가 부분 수열 길이."""
    if not a: return 0
    dp = [1] * len(a)
    for i in range(len(a)):
        for j in range(i):
            if a[j] < a[i] and dp[j] + 1 > dp[i]:
                dp[i] = dp[j] + 1
    return max(dp)


def lis_nlogn(a):
    """tails[k] = 길이 k+1인 증가 수열의 가장 작은 끝값. 이진 탐색으로 갱신. 수열도 복원."""
    tails, tails_idx, prev = [], [], [-1] * len(a)
    for i, x in enumerate(a):
        k = bisect.bisect_left(tails, x)          # 엄격 증가: bisect_left
        if k == len(tails):
            tails.append(x); tails_idx.append(i)
        else:
            tails[k] = x; tails_idx[k] = i
        prev[i] = tails_idx[k - 1] if k > 0 else -1
    seq, i = [], tails_idx[-1] if tails_idx else -1
    while i != -1:
        seq.append(a[i]); i = prev[i]
    return len(tails), seq[::-1]


def lcs(s, t):
    """가장 긴 공통 부분 수열 길이와 하나의 예."""
    n, m = len(s), len(t)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if s[i - 1] == t[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    out, i, j = [], n, m                          # 표를 거꾸로 따라가며 복원
    while i and j:
        if s[i - 1] == t[j - 1]:
            out.append(s[i - 1]); i -= 1; j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return dp[n][m], "".join(reversed(out))


def edit_distance(s, t):
    """삽입·삭제·교체 각 비용 1로 s를 t로 바꾸는 최소 연산 수 (레벤슈타인 거리)."""
    prev = list(range(len(t) + 1))
    for i in range(1, len(s) + 1):
        cur = [i] + [0] * len(t)
        for j in range(1, len(t) + 1):
            cur[j] = min(prev[j] + 1,                       # 삭제
                         cur[j - 1] + 1,                    # 삽입
                         prev[j - 1] + (s[i - 1] != t[j - 1]))   # 교체(같으면 0)
        prev = cur
    return prev[-1]


def edit_distance_bfs(s, t, alphabet):
    """검증용: 한 번 편집으로 갈 수 있는 문자열을 BFS로 탐색."""
    from collections import deque
    seen, q = {s: 0}, deque([s])
    while q:
        x = q.popleft()
        if x == t: return seen[x]
        if len(x) > max(len(s), len(t)) + 1: continue   # 이보다 긴 중간 문자열은 최단 경로에 필요 없다
        nxt = set()
        for i in range(len(x) + 1):
            for c in alphabet: nxt.add(x[:i] + c + x[i:])
            if i < len(x):
                nxt.add(x[:i] + x[i + 1:])
                for c in alphabet: nxt.add(x[:i] + c + x[i + 1:])
        for y in nxt:
            if y not in seen: seen[y] = seen[x] + 1; q.append(y)


if __name__ == "__main__":
    rng = random.Random(71)
    for _ in range(300):
        a = [rng.randint(0, 20) for _ in range(rng.randint(0, 12))]
        brute = max((len(c) for k in range(len(a) + 1) for c in itertools.combinations(a, k)
                     if all(c[i] < c[i + 1] for i in range(len(c) - 1))), default=0)
        L, seq = lis_nlogn(a)
        assert lis_n2(a) == L == brute
        assert len(seq) == L and all(seq[i] < seq[i + 1] for i in range(len(seq) - 1))
        it = iter(a); assert all(x in it for x in seq)        # seq가 a의 부분 수열인지
    print("LIS O(n^2)·O(n log n)·복원: 300개 입력에서 완전 탐색과 일치")
    print("LIS [10, 20, 10, 30, 20, 50] ->", lis_nlogn([10, 20, 10, 30, 20, 50]))

    for _ in range(300):
        s = "".join(rng.choice("ab") for _ in range(rng.randint(0, 8)))
        t = "".join(rng.choice("ab") for _ in range(rng.randint(0, 8)))
        L, w = lcs(s, t)
        brute = max(len(c) for k in range(len(s) + 1) for c in itertools.combinations(s, k)
                    if (lambda it: all(ch in it for ch in c))(iter(t)))
        assert L == brute == len(w)
    print("LCS: 300개 입력에서 완전 탐색과 일치. ACAYKP / CAPCAK ->", lcs("ACAYKP", "CAPCAK"))

    for _ in range(150):
        s = "".join(rng.choice("ab") for _ in range(rng.randint(0, 4)))
        t = "".join(rng.choice("ab") for _ in range(rng.randint(0, 4)))
        assert edit_distance(s, t) == edit_distance_bfs(s, t, "ab")
    print("편집 거리: 150개 입력에서 BFS 최단 편집 수와 일치. kitten -> sitting =", edit_distance("kitten", "sitting"))
