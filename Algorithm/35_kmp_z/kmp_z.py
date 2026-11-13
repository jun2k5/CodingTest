"""문자열 검색: 단순 비교, KMP(실패 함수), Z 알고리즘. 모두 패턴이 나오는 모든 시작 위치를 반환한다."""
import random


def naive_search(t, p):
    """반환: (위치 목록, 문자 비교 횟수)."""
    res, cmp_ = [], 0
    for i in range(len(t) - len(p) + 1):
        j = 0
        while j < len(p):
            cmp_ += 1
            if t[i + j] != p[j]: break
            j += 1
        if j == len(p): res.append(i)
    return res, cmp_


def failure(p):
    """fail[i] = p[:i+1]의 접두사이면서 접미사인 가장 긴 문자열 길이 (자기 자신 제외)."""
    fail = [0] * len(p)
    j = 0
    for i in range(1, len(p)):
        while j and p[i] != p[j]:
            j = fail[j - 1]
        if p[i] == p[j]:
            j += 1
            fail[i] = j
    return fail


def kmp_search(t, p):
    """불일치가 나면 패턴을 fail 값만큼만 되돌린다. 텍스트 포인터는 뒤로 가지 않는다."""
    if not p: return list(range(len(t) + 1)), 0
    fail, res, j, cmp_ = failure(p), [], 0, 0
    for i, c in enumerate(t):
        while j and c != p[j]:
            cmp_ += 1
            j = fail[j - 1]
        cmp_ += 1
        if c == p[j]:
            j += 1
            if j == len(p):
                res.append(i - len(p) + 1)
                j = fail[j - 1]
    return res, cmp_


def z_array(s):
    """z[i] = s와 s[i:]의 가장 긴 공통 접두사 길이. [l, r) = 지금까지 찾은 가장 오른쪽 Z 상자."""
    n = len(s)
    z = [0] * n
    if n: z[0] = n
    l = r = 0
    for i in range(1, n):
        if i < r:
            z[i] = min(r - i, z[i - l])            # 상자 안이면 이미 아는 값 재사용
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] > r:
            l, r = i, i + z[i]
    return z


def z_search(t, p, sep="\x00"):
    """p + 구분자 + t의 Z 배열에서 값이 len(p)인 위치."""
    if not p: return list(range(len(t) + 1))
    z = z_array(p + sep + t)
    m = len(p)
    return [i - m - 1 for i in range(m + 1, len(z)) if z[i] >= m]


def z_brute(s):
    out = []
    for i in range(len(s)):
        k = 0
        while i + k < len(s) and s[k] == s[i + k]: k += 1
        out.append(k)
    return out


def all_find(t, p):
    res, i = [], t.find(p)
    while i != -1:
        res.append(i); i = t.find(p, i + 1)
    return res


if __name__ == "__main__":
    rng = random.Random(35)
    for _ in range(2000):
        t = "".join(rng.choice("ab") for _ in range(rng.randint(0, 40)))
        p = "".join(rng.choice("ab") for _ in range(rng.randint(1, 5)))
        ref = all_find(t, p)
        assert naive_search(t, p)[0] == kmp_search(t, p)[0] == z_search(t, p) == ref
        s = t + p
        assert z_array(s) == z_brute(s)
        fb = [max((k for k in range(i + 1) if p[:k] == p[i + 1 - k:i + 1]), default=0) for i in range(len(p))]
        assert failure(p) == fb
    print("단순 비교·KMP·Z 검색: 2000개 입력에서 str.find로 찾은 모든 위치와 일치, 실패 함수·Z 배열도 정의대로 계산한 값과 일치")

    print("failure('ABABCABAB') =", failure("ABABCABAB"))
    print("failure('AABAAAB')   =", failure("AABAAAB"))
    print("z_array('aabxaab')   =", z_array("aabxaab"))
    # 백준 1786 찾기 예제
    t, p = "ABC ABCDAB ABCDABCDABDE", "ABCDABD"
    print("백준 1786 예제: 위치(1부터)", [i + 1 for i in kmp_search(t, p)[0]])

    # 비교 횟수: 최악 입력 (aaa...a 에서 aaa...ab 찾기)
    for n, m in ((10000, 100), (100000, 1000)):
        t = "a" * n
        p = "a" * (m - 1) + "b"
        _, c1 = naive_search(t, p)
        _, c2 = kmp_search(t, p)
        print(f"텍스트 a*{n:,}, 패턴 a*{m - 1}+b: 단순 비교 {c1:,}번, KMP {c2:,}번")
