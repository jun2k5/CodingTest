"""거듭제곱과 순환: 반복 이진 거듭제곱, 행렬 거듭제곱(피보나치·선형 점화식), 플로이드 순환 탐지, 브렌트."""
import random

MOD = 1_000_000_007


def mod_pow(a, e, m):
    """지수를 2진수로 보고, 비트가 1인 자리의 a^(2^k)만 곱한다. 곱셈 O(log e)번."""
    result, a = 1 % m, a % m
    while e:
        if e & 1: result = result * a % m
        a = a * a % m
        e >>= 1
    return result


def mat_mul(A, B, m):
    n, k, p = len(A), len(B), len(B[0])
    return [[sum(A[i][t] * B[t][j] for t in range(k)) % m for j in range(p)] for i in range(n)]


def mat_pow(M, e, m):
    n = len(M)
    R = [[int(i == j) for j in range(n)] for i in range(n)]
    while e:
        if e & 1: R = mat_mul(R, M, m)
        M = mat_mul(M, M, m)
        e >>= 1
    return R


def fib_matrix(n, m=MOD):
    """[[1,1],[1,0]]^n = [[F(n+1), F(n)], [F(n), F(n-1)]]."""
    return mat_pow([[1, 1], [1, 0]], n, m)[0][1]


def linear_recurrence(coef, init, n, m=MOD):
    """a(k) = coef[0]·a(k-1) + ... + coef[d-1]·a(k-d). init = [a(0), ..., a(d-1)]. 동반 행렬의 거듭제곱."""
    d = len(coef)
    if n < d: return init[n] % m
    T = [coef[:]] + [[int(j == i) for j in range(d)] for i in range(d - 1)]
    P = mat_pow(T, n - d + 1, m)
    state = init[::-1]                             # [a(d-1), ..., a(0)]
    return sum(P[0][j] * state[j] for j in range(d)) % m


def floyd_cycle(f, x0):
    """거북이는 1칸, 토끼는 2칸. 만나면 순환 안. 거북이를 시작점으로 돌리고 둘 다 1칸씩 → 다시 만나는 곳이 순환 시작.
    반환: (mu = 순환 시작 인덱스, lam = 순환 길이). 메모리 O(1)."""
    tortoise, hare = f(x0), f(f(x0))
    while tortoise != hare:
        tortoise, hare = f(tortoise), f(f(hare))
    mu, tortoise = 0, x0
    while tortoise != hare:
        tortoise, hare = f(tortoise), f(hare); mu += 1
    lam, hare = 1, f(tortoise)
    while tortoise != hare:
        hare = f(hare); lam += 1
    return mu, lam


def brent_cycle(f, x0):
    """토끼가 2의 거듭제곱 길이 구간마다 거북이를 순간이동시킨다. f 호출이 플로이드보다 적다."""
    power = lam = 1
    tortoise, hare = x0, f(x0)
    while tortoise != hare:
        if power == lam:
            tortoise, power, lam = hare, power * 2, 0
        hare = f(hare); lam += 1
    tortoise = hare = x0
    for _ in range(lam): hare = f(hare)
    mu = 0
    while tortoise != hare:
        tortoise, hare = f(tortoise), f(hare); mu += 1
    return mu, lam


def cycle_by_dict(f, x0):
    seen, x, i = {}, x0, 0
    while x not in seen:
        seen[x] = i; x = f(x); i += 1
    return seen[x], i - seen[x]


class Counter:
    def __init__(self, f): self.f, self.calls = f, 0
    def __call__(self, x): self.calls += 1; return self.f(x)


if __name__ == "__main__":
    rng = random.Random(41)
    for _ in range(3000):
        a, e, m = rng.randint(0, 10**12), rng.randint(0, 10**12), rng.randint(1, 10**9)
        assert mod_pow(a, e, m) == pow(a, e, m)
    print("반복 이진 거듭제곱: 3000개 입력에서 pow(a, e, m)과 일치")

    fib = [0, 1]
    for _ in range(500): fib.append(fib[-1] + fib[-2])
    assert all(fib_matrix(n) == fib[n] % MOD for n in range(500))
    for _ in range(200):
        d = rng.randint(1, 4)
        coef = [rng.randint(-3, 3) for _ in range(d)]
        init = [rng.randint(-5, 5) for _ in range(d)]
        seq = init[:]
        for k in range(d, 60): seq.append(sum(coef[j] * seq[k - 1 - j] for j in range(d)))
        n = rng.randint(0, 59)
        assert linear_recurrence(coef, init, n) == seq[n] % MOD
    print("행렬 거듭제곱: 피보나치 0~499, 무작위 선형 점화식 200개에서 직접 계산과 일치")
    print("F(10^18) mod 1,000,000,007 =", fib_matrix(10**18))
    print("트리보나치 T(n)=T(n-1)+T(n-2)+T(n-3), T(0..2)=0,0,1 -> T(10) =", linear_recurrence([1, 1, 1], [0, 0, 1], 10),
          ", T(10^15) mod p =", linear_recurrence([1, 1, 1], [0, 0, 1], 10**15))

    for _ in range(1000):
        m = rng.randint(1, 2000)
        table = [rng.randrange(m) for _ in range(m)]
        f = table.__getitem__
        x0 = rng.randrange(m)
        assert floyd_cycle(f, x0) == brent_cycle(f, x0) == cycle_by_dict(f, x0)
    print("플로이드·브렌트 순환 탐지: 1000개 무작위 함수에서 딕셔너리 방문 기록과 (시작, 길이) 일치")

    f = lambda x: (x * x + 1) % 255
    seq = [3]
    for _ in range(8): seq.append(f(seq[-1]))
    print("x -> x²+1 mod 255, x0=3: 수열", seq, "→ (시작, 길이) =", floyd_cycle(f, 3))
    for m in (10**6, 10**8):
        g = lambda x, m=m: (x * x + 12345) % m
        cf, cb = Counter(g), Counter(g)
        r1, r2 = floyd_cycle(cf, 7), brent_cycle(cb, 7)
        assert r1 == r2
        print(f"x -> x²+12345 mod {m:,}: (시작, 길이) = {r1}, f 호출 플로이드 {cf.calls:,}번 / 브렌트 {cb.calls:,}번")
