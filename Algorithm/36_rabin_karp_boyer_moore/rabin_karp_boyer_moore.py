"""문자열 검색: 라빈-카프(롤링 해시), 보이어-무어(나쁜 문자 + 착한 접미사), 호스풀."""
import random


def rabin_karp(t, p, base=256, mod=(1 << 61) - 1):
    """반환: (위치 목록, 해시가 같았지만 실제로는 다른 경우의 수)."""
    n, m = len(t), len(p)
    if m > n: return [], 0
    if m == 0: return list(range(n + 1)), 0
    high = pow(base, m - 1, mod)                 # 맨 앞 문자의 자릿값
    hp = ht = 0
    for i in range(m):
        hp = (hp * base + ord(p[i])) % mod
        ht = (ht * base + ord(t[i])) % mod
    res, false_hit = [], 0
    for i in range(n - m + 1):
        if hp == ht:
            if t[i:i + m] == p: res.append(i)    # 해시가 같으면 실제로 비교해 확인
            else: false_hit += 1
        if i + m < n:                            # 맨 앞 문자를 빼고 새 문자를 더한다
            ht = ((ht - ord(t[i]) * high) * base + ord(t[i + m])) % mod
    return res, false_hit


def bad_char_table(p):
    """문자별로 패턴에서 마지막으로 나온 위치."""
    return {c: i for i, c in enumerate(p)}


def good_suffix_table(p):
    """shift[j] = 패턴의 p[j:]가 맞고 p[j-1]에서 틀렸을 때 밀 수 있는 거리 (강한 착한 접미사 규칙)."""
    m = len(p)
    shift, border = [0] * (m + 1), [0] * (m + 1)
    i, j = m, m + 1
    border[i] = j
    while i > 0:
        while j <= m and p[i - 1] != p[j - 1]:
            if shift[j] == 0: shift[j] = j - i
            j = border[j]
        i -= 1; j -= 1
        border[i] = j
    j = border[0]
    for i in range(m + 1):
        if shift[i] == 0: shift[i] = j
        if i == j: j = border[j]
    return shift


def boyer_moore(t, p):
    """패턴을 오른쪽 끝부터 비교한다. 틀리면 두 규칙 중 더 멀리 미는 쪽을 쓴다. 반환: (위치, 비교 횟수)."""
    n, m = len(t), len(p)
    if m == 0: return list(range(n + 1)), 0
    last, gs = bad_char_table(p), good_suffix_table(p)
    res, s, cmp_ = [], 0, 0
    while s <= n - m:
        j = m - 1
        while j >= 0:
            cmp_ += 1
            if p[j] != t[s + j]: break
            j -= 1
        if j < 0:
            res.append(s); s += gs[0]
        else:
            s += max(gs[j + 1], j - last.get(t[s + j], -1))
    return res, cmp_


def horspool(t, p):
    """보이어-무어 단순화: 창 맨 끝 문자로만 이동 거리를 정한다."""
    n, m = len(t), len(p)
    if m == 0: return list(range(n + 1)), 0
    skip = {c: m - 1 - i for i, c in enumerate(p[:-1])}
    res, s, cmp_ = [], 0, 0
    while s <= n - m:
        j = m - 1
        while j >= 0:
            cmp_ += 1
            if p[j] != t[s + j]: break
            j -= 1
        if j < 0: res.append(s)
        s += skip.get(t[s + m - 1], m)
    return res, cmp_


def naive_cmp(t, p):
    c = 0
    for i in range(len(t) - len(p) + 1):
        for j in range(len(p)):
            c += 1
            if t[i + j] != p[j]: break
    return c


def all_find(t, p):
    res, i = [], t.find(p)
    while i != -1:
        res.append(i); i = t.find(p, i + 1)
    return res


if __name__ == "__main__":
    rng = random.Random(36)
    for _ in range(3000):
        alpha = rng.choice(["ab", "abc", "abcdefgh"])
        t = "".join(rng.choice(alpha) for _ in range(rng.randint(0, 60)))
        p = "".join(rng.choice(alpha) for _ in range(rng.randint(1, 6)))
        ref = all_find(t, p)
        assert rabin_karp(t, p)[0] == boyer_moore(t, p)[0] == horspool(t, p)[0] == ref, (t, p)
        assert rabin_karp(t, p, base=31, mod=7)[0] == ref        # 작은 mod: 충돌이 많아도 확인 단계 덕분에 정답
    print("라빈-카프·보이어-무어·호스풀: 3000개 입력에서 str.find로 찾은 모든 위치와 일치")

    # 해시 충돌: 작은 mod에서는 가짜 일치가 많다
    t = "".join(rng.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(100000))
    p = "algorithm"
    for mod in (101, 10007, (1 << 61) - 1):
        r, fh = rabin_karp(t, p, mod=mod)
        print(f"무작위 소문자 100,000자에서 '{p}' 검색, mod={mod}: 실제 일치 {len(r)}번, 해시만 같은 경우 {fh:,}번")

    # 비교 횟수: 알파벳이 클수록 보이어-무어가 많이 건너뛴다
    words = ("the quick brown fox jumps over the lazy dog while the algorithm "
             "searches for patterns in a long text made of ordinary english words ").split()
    text = " ".join(rng.choice(words) for _ in range(20000))
    for p in ("algorithm", "patterns in a long"):
        print(f"영어 단어 텍스트 {len(text):,}자에서 '{p}': 단순 {naive_cmp(text, p):,}번, "
              f"호스풀 {horspool(text, p)[1]:,}번, 보이어-무어 {boyer_moore(text, p)[1]:,}번 비교")
    dna = "".join(rng.choice("ACGT") for _ in range(len(text)))
    for p in ("ACGTTGCA", "GCAGAGAG"):
        print(f"DNA(ACGT) {len(dna):,}자에서 '{p}': 단순 {naive_cmp(dna, p):,}번, "
              f"호스풀 {horspool(dna, p)[1]:,}번, 보이어-무어 {boyer_moore(dna, p)[1]:,}번 비교")
    print("good_suffix_table('ANPANMAN') =", good_suffix_table("ANPANMAN"))
