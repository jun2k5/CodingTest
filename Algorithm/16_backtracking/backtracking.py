"""브루트포스와 백트래킹: 순열·조합, N-Queen, 부분집합(비트마스크), 가지치기 효과."""
import itertools, random


def permutations(arr, r):
    out, used, cur = [], [False] * len(arr), []
    def go():
        if len(cur) == r:
            out.append(tuple(cur)); return
        for i, x in enumerate(arr):
            if not used[i]:
                used[i] = True; cur.append(x)
                go()
                cur.pop(); used[i] = False         # 되돌리기(backtrack)
    go()
    return out


def combinations(arr, r):
    out, cur = [], []
    def go(start):
        if len(cur) == r:
            out.append(tuple(cur)); return
        for i in range(start, len(arr)):            # start부터: 같은 조합을 순서만 바꿔 다시 고르지 않는다
            cur.append(arr[i]); go(i + 1); cur.pop()
    go(0)
    return out


def subsets_bitmask(arr):
    n = len(arr)
    return [tuple(arr[i] for i in range(n) if mask >> i & 1) for mask in range(1 << n)]


def n_queens(n):
    """해의 개수와 방문한 노드 수(가지치기 효과 측정용)."""
    cols, d1, d2 = [False] * n, [False] * (2 * n), [False] * (2 * n)
    count, visited = 0, 0
    def go(row):
        nonlocal count, visited
        visited += 1
        if row == n:
            count += 1; return
        for c in range(n):
            if cols[c] or d1[row + c] or d2[row - c + n]:
                continue                            # 이미 공격받는 칸은 더 내려가지 않는다(가지치기)
            cols[c] = d1[row + c] = d2[row - c + n] = True
            go(row + 1)
            cols[c] = d1[row + c] = d2[row - c + n] = False
    go(0)
    return count, visited


def n_queens_brute(n):
    """행마다 열 하나씩 고르는 모든 배치(n^n)를 만든 뒤 검사."""
    cnt = 0
    for cols in itertools.product(range(n), repeat=n):
        ok = all(cols[i] != cols[j] and abs(cols[i] - cols[j]) != j - i for i in range(n) for j in range(i + 1, n))
        cnt += ok
    return cnt


def subset_sum_count(arr, target):
    """합이 target인 부분집합 개수 (원소 양수, 정렬 후 초과하면 가지치기)."""
    arr = sorted(arr)
    count, nodes = 0, 0
    def go(i, s):
        nonlocal count, nodes
        nodes += 1
        if s == target:
            count += 1
        for j in range(i, len(arr)):
            if s + arr[j] > target:
                break                               # 정렬돼 있으니 뒤도 전부 초과
            go(j + 1, s + arr[j])
    go(0, 0)
    return count, nodes


if __name__ == "__main__":
    rng = random.Random(47)
    for _ in range(100):
        arr = list(range(rng.randint(0, 6)))
        r = rng.randint(0, len(arr))
        assert permutations(arr, r) == list(itertools.permutations(arr, r))
        assert combinations(arr, r) == list(itertools.combinations(arr, r))
        assert sorted(subsets_bitmask(arr)) == sorted(c for k in range(len(arr) + 1) for c in itertools.combinations(arr, k))
    print("순열·조합·부분집합: itertools와 100개 입력에서 일치")

    print("N-Queen 해의 개수:", {n: n_queens(n)[0] for n in range(1, 11)})
    for n in (6, 7):
        assert n_queens(n)[0] == n_queens_brute(n)
    for n in (8, 10, 12):
        c, v = n_queens(n)
        print(f"N={n}: 해 {c}개, 백트래킹 방문 노드 {v:,}개, 단순 완전 탐색 배치 수 {n**n:,}개")

    for _ in range(200):
        arr = [rng.randint(1, 10) for _ in range(rng.randint(0, 10))]
        t = rng.randint(0, 30)
        brute = sum(1 for m in range(1 << len(arr)) if sum(arr[i] for i in range(len(arr)) if m >> i & 1) == t)
        assert subset_sum_count(arr, t)[0] == brute
    arr = [rng.randint(1, 50) for _ in range(20)]
    c, nodes = subset_sum_count(arr, 60)
    print(f"원소 20개 부분집합 합=60: {c}개, 방문 노드 {nodes:,} / 전체 부분집합 {1 << 20:,}")
