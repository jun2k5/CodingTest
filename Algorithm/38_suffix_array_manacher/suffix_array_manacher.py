"""접미사 배열(접두사 두 배 늘리기), LCP 배열(카사이), 매내처(모든 위치의 회문 반지름)."""
import random


def suffix_array(s):
    """길이 k 접두사의 순위로 정렬하고, (rank[i], rank[i+k])로 길이 2k 순위를 만든다. O(n log² n)."""
    n = len(s)
    if n == 0: return []
    sa = list(range(n))
    rank = [ord(c) for c in s]
    k = 1
    while True:
        key = lambda i: (rank[i], rank[i + k] if i + k < n else -1)
        sa.sort(key=key)
        new = [0] * n
        for a, b in zip(sa, sa[1:]):
            new[b] = new[a] + (key(a) != key(b))
        rank = new
        if rank[sa[-1]] == n - 1: break          # 모든 순위가 다르면 끝
        k *= 2
    return sa


def lcp_array(s, sa):
    """카사이: lcp[i] = sa[i]와 sa[i-1] 접미사의 공통 접두사 길이. 원래 문자열 순서로 돌면 h가 1씩만 줄어 O(n)."""
    n = len(s)
    rank = [0] * n
    for i, p in enumerate(sa): rank[p] = i
    lcp, h = [0] * n, 0
    for i in range(n):
        if rank[i] > 0:
            j = sa[rank[i] - 1]
            while i + h < n and j + h < n and s[i + h] == s[j + h]:
                h += 1
            lcp[rank[i]] = h
            if h: h -= 1
        else:
            h = 0
    return lcp


def distinct_substrings(s):
    """서로 다른 부분 문자열 수 = 전체 n(n+1)/2 - 인접 접미사가 겹치는 접두사 수(Σ lcp)."""
    sa = suffix_array(s)
    return len(s) * (len(s) + 1) // 2 - sum(lcp_array(s, sa))


def manacher(s):
    """문자 사이에 '#'을 넣어 짝수·홀수 회문을 같이 다룬다. p[i] = i 중심 회문 반지름(변환 문자열 기준).
    [c - p[c], c + p[c]]: 지금까지 가장 오른쪽까지 닿은 회문. 그 안이면 대칭 위치 값부터 시작한다."""
    t = "#" + "#".join(s) + "#"
    n = len(t)
    p = [0] * n
    c = r = 0
    for i in range(n):
        if i < r:
            p[i] = min(r - i, p[2 * c - i])
        while i - p[i] - 1 >= 0 and i + p[i] + 1 < n and t[i - p[i] - 1] == t[i + p[i] + 1]:
            p[i] += 1
        if i + p[i] > r:
            c, r = i, i + p[i]
    return p                                      # 원래 문자열에서 회문 길이 = p[i]


def longest_palindrome(s):
    if not s: return ""
    p = manacher(s)
    i = max(range(len(p)), key=lambda k: p[k])
    start = (i - p[i]) // 2
    return s[start:start + p[i]]


def manacher_brute(s):
    t = "#" + "#".join(s) + "#"
    out = []
    for i in range(len(t)):
        k = 0
        while i - k - 1 >= 0 and i + k + 1 < len(t) and t[i - k - 1] == t[i + k + 1]: k += 1
        out.append(k)
    return out


if __name__ == "__main__":
    rng = random.Random(38)
    for _ in range(1500):
        s = "".join(rng.choice(rng.choice(["ab", "abc", "abcdz"])) for _ in range(rng.randint(0, 40)))
        sa = suffix_array(s)
        assert sa == sorted(range(len(s)), key=lambda i: s[i:])
        lcp = lcp_array(s, sa)
        for i in range(1, len(s)):
            a, b = s[sa[i]:], s[sa[i - 1]:]
            k = 0
            while k < min(len(a), len(b)) and a[k] == b[k]: k += 1
            assert lcp[i] == k
        assert distinct_substrings(s) == len({s[i:j] for i in range(len(s)) for j in range(i + 1, len(s) + 1)})
        assert manacher(s) == manacher_brute(s)
        lp = longest_palindrome(s)
        best = max((len(s[i:j]) for i in range(len(s)) for j in range(i + 1, len(s) + 1) if s[i:j] == s[i:j][::-1]), default=0)
        assert len(lp) == best and lp == lp[::-1] and lp in s
    print("접미사 배열·LCP·서로 다른 부분 문자열 수·매내처: 1500개 입력에서 정의대로 계산한 값과 일치")

    s = "banana"
    sa = suffix_array(s)
    lcp = lcp_array(s, sa)
    for i, p in enumerate(sa):
        print(f"  sa[{i}]={p}  lcp={lcp[i]}  {s[p:]}")
    print("banana의 서로 다른 부분 문자열:", distinct_substrings(s))
    print("manacher('abaaba') =", manacher("abaaba"))
    for w in ("babad", "forgeeksskeegfor", "abacdfgdcaba"):
        print(f"가장 긴 회문 부분 문자열 {w!r} -> {longest_palindrome(w)!r}")

    import time
    s = "".join(rng.choice("ab") for _ in range(200000))
    t0 = time.perf_counter(); p = manacher(s); t1 = time.perf_counter()
    sa = suffix_array(s); t2 = time.perf_counter(); lcp_array(s, sa); t3 = time.perf_counter()
    print(f"길이 200,000 문자열: 매내처 {1000 * (t1 - t0):.0f}ms, 접미사 배열 {1000 * (t2 - t1):.0f}ms, LCP {1000 * (t3 - t2):.0f}ms")
