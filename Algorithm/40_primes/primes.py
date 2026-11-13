"""소수: 시행 나눗셈, 에라토스테네스의 체, 선형 체(최소 소인수), 소인수분해, 밀러-라빈, 폴라드 로."""
import math, random, time


def is_prime_trial(n):
    """√n까지만 나눠 보면 된다. n = a*b이면 둘 중 하나는 √n 이하."""
    if n < 2: return False
    if n % 2 == 0: return n == 2
    i = 3
    while i * i <= n:
        if n % i == 0: return False
        i += 2
    return True


def sieve(n):
    """i가 소수이면 i*i부터 i의 배수를 지운다(그보다 작은 배수는 더 작은 소인수가 이미 지웠다)."""
    is_p = bytearray([1]) * (n + 1)
    is_p[0:2] = b"\x00\x00"[: min(2, n + 1)]
    for i in range(2, math.isqrt(n) + 1):
        if is_p[i]:
            is_p[i * i::i] = bytes(len(range(i * i, n + 1, i)))
    return is_p


def linear_sieve(n):
    """각 합성수를 '최소 소인수 × 나머지'로 정확히 한 번만 지운다. spf[x] = x의 최소 소인수."""
    spf = [0] * (n + 1)
    primes = []
    for i in range(2, n + 1):
        if spf[i] == 0:
            spf[i] = i; primes.append(i)
        for p in primes:
            if p > spf[i] or i * p > n: break
            spf[i * p] = p
    return primes, spf


def factorize_spf(x, spf):
    out = []
    while x > 1:
        out.append(spf[x]); x //= spf[x]
    return out


def factorize_trial(n):
    out, d = [], 2
    while d * d <= n:
        while n % d == 0:
            out.append(d); n //= d
        d += 1
    if n > 1: out.append(n)
    return out


def miller_rabin(n):
    """n-1 = d·2^s. 밑 a에 대해 a^d ≡ 1 이거나 어떤 r < s에서 a^(d·2^r) ≡ -1 이어야 소수 후보.
    아래 12개 밑이면 n < 3.1·10^23 범위(64비트 정수 전체 포함)에서 결정적으로 맞다."""
    if n < 2: return False
    small = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for p in small:
        if n % p == 0: return n == p
    d, s = n - 1, 0
    while d % 2 == 0: d //= 2; s += 1
    for a in small:
        x = pow(a, d, n)
        if x in (1, n - 1): continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1: break
        else:
            return False                          # a가 n이 합성수라는 증인
    return True


def pollard_rho(n):
    """f(x) = x² + c mod n 수열에서 플로이드 순환 탐지(41번)로 gcd(|x - y|, n) > 1인 순간을 찾는다."""
    if n % 2 == 0: return 2
    while True:
        c = random.randrange(1, n)
        f = lambda v: (v * v + c) % n
        x = y = random.randrange(2, n)
        d = 1
        while d == 1:
            x = f(x); y = f(f(y))
            d = math.gcd(abs(x - y), n)
        if d != n: return d


def factorize_big(n):
    if n == 1: return []
    if miller_rabin(n): return [n]
    d = pollard_rho(n)
    return sorted(factorize_big(d) + factorize_big(n // d))


if __name__ == "__main__":
    rng = random.Random(40)
    random.seed(40)
    N = 100000
    s = sieve(N)
    primes, spf = linear_sieve(N)
    ref = [i for i in range(N + 1) if is_prime_trial(i)]
    assert [i for i in range(N + 1) if s[i]] == ref == primes
    assert all(miller_rabin(i) == bool(s[i]) for i in range(N + 1))
    for x in range(2, N + 1):
        assert factorize_spf(x, spf) == factorize_trial(x)
    print(f"{N:,} 이하: 체·선형 체·밀러-라빈·시행 나눗셈 판정 일치(소수 {len(ref):,}개), 최소 소인수 분해 = 시행 나눗셈 분해")

    # 큰 수: 밀러-라빈 vs 시행 나눗셈 (10^12 근처), 카마이클 수
    for _ in range(300):
        n = rng.randint(10**11, 10**12)
        assert miller_rabin(n) == is_prime_trial(n)
    carm = [561, 1105, 1729, 2465, 2821, 6601, 8911]
    print("카마이클 수(페르마 판정을 속이는 합성수) 밀러-라빈 판정:", [miller_rabin(c) for c in carm],
          " 페르마(밑 2) 판정:", [pow(2, c - 1, c) == 1 for c in carm])
    for n in (10**18 + 3, 10**18 + 9, 2**61 - 1, 2**89 - 1):
        t0 = time.perf_counter(); r = miller_rabin(n); t1 = time.perf_counter()
        print(f"  {n}: 소수 {r} ({1e6 * (t1 - t0):.0f}μs)")

    for _ in range(100):
        n = rng.randint(2, 10**12)
        assert factorize_big(n) == factorize_trial(n)
    n = 1000000007 * 998244353
    t0 = time.perf_counter(); f = factorize_big(n); t1 = time.perf_counter()
    print(f"폴라드 로: 100개 수(10^12 이하)에서 시행 나눗셈 분해와 일치 / {n} = {f} ({1000 * (t1 - t0):.1f}ms)")

    for n in (10**6, 10**7):
        t0 = time.perf_counter(); c1 = sum(sieve(n)); t1 = time.perf_counter()
        print(f"에라토스테네스의 체 n={n:,}: 소수 {c1:,}개, {1000 * (t1 - t0):.0f}ms")
    t0 = time.perf_counter(); c3 = sum(1 for i in range(2 * 10**5) if is_prime_trial(i)); t1 = time.perf_counter()
    t2 = time.perf_counter(); c4 = sum(sieve(2 * 10**5)); t3 = time.perf_counter()
    print(f"20만 이하 소수 {c3:,}개: 수마다 시행 나눗셈 {1000 * (t1 - t0):.0f}ms, 체 {1000 * (t3 - t2):.1f}ms")
