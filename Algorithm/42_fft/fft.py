"""고속 푸리에 변환: 재귀 FFT, 반복 FFT(비트 반전), 다항식 곱셈, NTT(정수 모듈러), 큰 수 곱셈."""
import cmath, random, time


def fft_recursive(a, invert=False):
    """짝수 번째 계수와 홀수 번째 계수로 나눠 각각 n/2 크기로 변환하고 합친다. len(a)는 2의 거듭제곱."""
    n = len(a)
    if n == 1: return a[:]
    even = fft_recursive(a[0::2], invert)
    odd = fft_recursive(a[1::2], invert)
    ang = (-2 if invert else 2) * cmath.pi / n
    out = [0] * n
    for k in range(n // 2):
        w = cmath.exp(1j * ang * k)
        out[k] = even[k] + w * odd[k]
        out[k + n // 2] = even[k] - w * odd[k]   # ω^(k + n/2) = -ω^k
    return out


def fft(a, invert=False, accumulate=False):
    """반복 버전: 비트 반전 순서로 재배치한 뒤 길이 2, 4, 8, ... 순서로 나비 연산."""
    a = list(a)
    n = len(a)
    j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit:
            j ^= bit; bit >>= 1
        j |= bit
        if i < j: a[i], a[j] = a[j], a[i]
    length = 2
    while length <= n:
        ang = (-2 if invert else 2) * cmath.pi / length
        half = length // 2
        if accumulate:                            # 비교용: w *= wl로 누적하면 반올림 오차가 쌓인다
            roots, w, wl = [], 1, cmath.exp(1j * ang)
            for _ in range(half): roots.append(w); w *= wl
        else:
            roots = [cmath.exp(1j * ang * k) for k in range(half)]
        for i in range(0, n, length):
            for k in range(half):
                u, v = a[i + k], a[i + k + half] * roots[k]
                a[i + k], a[i + k + half] = u + v, u - v
        length <<= 1
    if invert:
        a = [x / n for x in a]
    return a


def multiply(p, q, accumulate=False):
    """계수 표현 → (FFT) 점 표현 → 점끼리 곱 → (역 FFT) 계수 표현. 정수 계수면 반올림."""
    if not p or not q: return []
    n = 1
    while n < len(p) + len(q) - 1: n <<= 1
    fp = fft(p + [0] * (n - len(p)), accumulate=accumulate)
    fq = fft(q + [0] * (n - len(q)), accumulate=accumulate)
    r = fft([x * y for x, y in zip(fp, fq)], invert=True, accumulate=accumulate)
    return [round(x.real) for x in r[:len(p) + len(q) - 1]]


def naive_multiply(p, q):
    if not p or not q: return []
    r = [0] * (len(p) + len(q) - 1)
    for i, x in enumerate(p):
        for j, y in enumerate(q):
            r[i + j] += x * y
    return r


MOD, G = 998244353, 3                             # 998244353 = 119·2^23 + 1, 원시근 3


def ntt(a, invert=False):
    """복소수 대신 mod p에서의 n제곱근을 쓴다. 실수 오차가 없다."""
    a = list(a)
    n = len(a)
    j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit:
            j ^= bit; bit >>= 1
        j |= bit
        if i < j: a[i], a[j] = a[j], a[i]
    length = 2
    while length <= n:
        wl = pow(G, (MOD - 1) // length, MOD)
        if invert: wl = pow(wl, MOD - 2, MOD)
        for i in range(0, n, length):
            w = 1
            half = length // 2
            for k in range(half):
                u, v = a[i + k], a[i + k + half] * w % MOD
                a[i + k] = (u + v) % MOD
                a[i + k + half] = (u - v) % MOD
                w = w * wl % MOD
        length <<= 1
    if invert:
        inv_n = pow(n, MOD - 2, MOD)
        a = [x * inv_n % MOD for x in a]
    return a


def multiply_ntt(p, q):
    if not p or not q: return []
    n = 1
    while n < len(p) + len(q) - 1: n <<= 1
    fp, fq = ntt(p + [0] * (n - len(p))), ntt(q + [0] * (n - len(q)))
    return ntt([x * y % MOD for x, y in zip(fp, fq)], invert=True)[:len(p) + len(q) - 1]


def big_multiply(x, y):
    """10진수 자릿수를 다항식 계수로 보고 곱한 뒤 받아올림."""
    a = [int(c) for c in reversed(str(x))]
    b = [int(c) for c in reversed(str(y))]
    r = multiply(a, b)
    carry, digits = 0, []
    for v in r:
        v += carry
        digits.append(v % 10); carry = v // 10
    while carry:
        digits.append(carry % 10); carry //= 10
    return int("".join(map(str, reversed(digits))))


if __name__ == "__main__":
    rng = random.Random(42)
    for _ in range(300):
        n = 1 << rng.randint(0, 6)
        a = [complex(rng.uniform(-5, 5), rng.uniform(-5, 5)) for _ in range(n)]
        r1, r2 = fft_recursive(a), fft(a)
        assert all(abs(x - y) < 1e-9 for x, y in zip(r1, r2))
        dft = [sum(a[t] * cmath.exp(2j * cmath.pi * k * t / n) for t in range(n)) for k in range(n)]
        assert all(abs(x - y) < 1e-8 for x, y in zip(r2, dft))
        back = fft(r2, invert=True)
        assert all(abs(x - y) < 1e-9 for x, y in zip(back, a))
    print("재귀 FFT = 반복 FFT = 정의대로 계산한 DFT, 역변환으로 원래 값 복원: 300개 입력")

    for _ in range(300):
        p = [rng.randint(-100, 100) for _ in range(rng.randint(0, 80))]
        q = [rng.randint(-100, 100) for _ in range(rng.randint(0, 80))]
        ref = naive_multiply(p, q)
        assert multiply(p, q) == ref
        assert multiply_ntt(p, q) == [x % MOD for x in ref]
    print("다항식 곱셈(FFT·NTT): 300개 입력에서 이중 반복문 곱셈과 일치")

    print("(1 + 2x + 3x²)(4 + 5x) =", multiply([1, 2, 3], [4, 5]))
    for _ in range(100):
        x, y = rng.randint(0, 10**300), rng.randint(0, 10**300)
        assert big_multiply(x, y) == x * y
    print("큰 수 곱셈: 300자리 이하 100쌍에서 Python int 곱셈과 일치")

    for n in (1000, 4000, 16000):
        p = [rng.randint(0, 9) for _ in range(n)]
        q = [rng.randint(0, 9) for _ in range(n)]
        t0 = time.perf_counter(); r1 = naive_multiply(p, q); t1 = time.perf_counter()
        r2 = multiply(p, q); t2 = time.perf_counter()
        r3 = multiply_ntt(p, q); t3 = time.perf_counter()
        assert r1 == r2 and [x % MOD for x in r1] == r3
        print(f"차수 {n:,} 다항식 두 개 곱: 단순 {1000 * (t1 - t0):,.0f}ms, FFT {1000 * (t2 - t1):,.0f}ms, NTT {1000 * (t3 - t2):,.0f}ms")

    # 실수 오차: 계수가 크면 FFT 반올림이 틀린다. 정답은 큰 정수 하나로 묶어 곱하는 방식(크로네커 치환)으로 구한다
    def exact_conv(p, q, bits=80):
        P = int("".join(format(v, f"0{bits // 4}x") for v in reversed(p)), 16)
        Q = int("".join(format(v, f"0{bits // 4}x") for v in reversed(q)), 16)
        R, mask, out = P * Q, (1 << bits) - 1, []
        for _ in range(len(p) + len(q) - 1):
            out.append(R & mask); R >>= bits
        return out
    for c in (10**3, 10**4, 10**5, 10**6):
        p = [rng.randint(0, c) for _ in range(1 << 15)]
        q = [rng.randint(0, c) for _ in range(1 << 15)]
        ref = exact_conv(p, q)
        wrong = sum(x != y for x, y in zip(multiply(p, q), ref))
        wrong_acc = sum(x != y for x, y in zip(multiply(p, q, accumulate=True), ref))
        print(f"길이 32,768, 계수 최대 {c:,}: 결과 최댓값 약 {max(ref):.1e}, 반올림이 틀린 계수 "
              f"{wrong:,}개 (회전 인자 누적 곱 방식 {wrong_acc:,}개) / {len(ref):,}개")
