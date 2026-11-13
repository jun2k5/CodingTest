"""최대공약수와 합동식: 유클리드 호제법, 확장 유클리드, 모듈러 역원, 중국인의 나머지 정리."""
import math, random


def gcd(a, b):
    """gcd(a, b) = gcd(b, a mod b). 반환값은 0 이상."""
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def gcd_steps(a, b):
    steps = 0
    while b:
        a, b = b, a % b; steps += 1
    return steps


def lcm(a, b):
    return 0 if a == 0 or b == 0 else abs(a // gcd(a, b) * b)


def ext_gcd(a, b):
    """a*x + b*y = g = gcd(a, b)인 (g, x, y). b*x' + (a mod b)*y' = g 에서 거꾸로 올라온다."""
    if b == 0:
        return (a, 1, 0) if a >= 0 else (-a, -1, 0)
    g, x, y = ext_gcd(b, a % b)
    return g, y, x - (a // b) * y


def mod_inverse(a, m):
    """a*x ≡ 1 (mod m). gcd(a, m) = 1일 때만 존재."""
    g, x, _ = ext_gcd(a % m, m)
    if g != 1: return None
    return x % m


def solve_linear_congruence(a, b, m):
    """a*x ≡ b (mod m)의 해를 (x0, 주기)로. gcd(a, m)이 b를 나누지 않으면 해가 없다."""
    g = gcd(a, m)
    if b % g: return None
    a, b, m2 = a // g, b // g, m // g
    return (b * mod_inverse(a % m2, m2)) % m2 if m2 > 1 else 0, m2


def crt(rems, mods):
    """x ≡ r_i (mod m_i)를 모두 만족하는 (x, lcm). 모듈러가 서로소가 아니어도 된다. 해가 없으면 None."""
    x, m = 0, 1
    for r, mi in zip(rems, mods):
        g, p, _ = ext_gcd(m, mi)                  # m*p ≡ g (mod mi)
        if (r - x) % g: return None
        step = (r - x) // g * p % (mi // g)       # x + m*t ≡ r (mod mi)를 t에 대해 푼다
        x += m * step
        m = m // g * mi
        x %= m
    return x, m


def crt_brute(rems, mods):
    L = 1
    for mi in mods: L = L * mi // math.gcd(L, mi)
    for x in range(L):
        if all(x % mi == r % mi for r, mi in zip(rems, mods)):
            return x, L
    return None


if __name__ == "__main__":
    rng = random.Random(39)
    for _ in range(5000):
        a, b = rng.randint(-10**6, 10**6), rng.randint(-10**6, 10**6)
        assert gcd(a, b) == math.gcd(a, b)
        assert lcm(a, b) == math.lcm(a, b)
        g, x, y = ext_gcd(a, b)
        assert g == math.gcd(a, b) and a * x + b * y == g
        m = rng.randint(2, 10**6)
        inv = mod_inverse(a, m)
        ref = pow(a, -1, m) if math.gcd(a, m) == 1 else None
        assert inv == ref
    print("gcd·lcm·확장 유클리드·모듈러 역원: 5000개 입력에서 math.gcd, math.lcm, pow(a, -1, m)과 일치")

    for _ in range(2000):
        a, b, m = rng.randint(0, 60), rng.randint(0, 60), rng.randint(1, 60)
        sols = [x for x in range(m) if (a * x - b) % m == 0]
        r = solve_linear_congruence(a, b, m)
        if not sols: assert r is None
        else:
            x0, period = r
            assert sols == list(range(x0 % period, m, period))
    print("일차 합동식 a·x ≡ b (mod m): 2000개 입력에서 0..m-1 전수 대입 결과와 일치")

    for _ in range(2000):
        k = rng.randint(1, 4)
        mods = [rng.randint(1, 30) for _ in range(k)]
        rems = [rng.randint(0, 40) for _ in range(k)]
        assert crt(rems, mods) == crt_brute(rems, mods), (rems, mods)
    print("중국인의 나머지 정리(서로소 아닌 경우 포함): 2000개 연립식에서 전수 탐색과 일치")

    print("gcd(1071, 1029) =", gcd(1071, 1029), " 단계:", gcd_steps(1071, 1029))
    print("ext_gcd(240, 46) =", ext_gcd(240, 46))
    print("3의 역원 mod 11 =", mod_inverse(3, 11), " 6의 역원 mod 9 =", mod_inverse(6, 9))
    print("x≡2 (mod 3), x≡3 (mod 5), x≡2 (mod 7) ->", crt([2, 3, 2], [3, 5, 7]))
    print("x≡1 (mod 4), x≡3 (mod 6) ->", crt([1, 3], [4, 6]), " / x≡1 (mod 4), x≡2 (mod 6) ->", crt([1, 2], [4, 6]))

    # 최악 입력: 연속한 피보나치 수 (라메의 정리)
    f = [1, 1]
    while len(f) < 90: f.append(f[-1] + f[-2])
    for k in (30, 60, 89):
        print(f"gcd(F{k + 1}, F{k}) = gcd({f[k]:,}, {f[k - 1]:,}) 단계 수: {gcd_steps(f[k], f[k - 1])}")
    big = [rng.randint(1, 10**18) for _ in range(20000)]
    avg = sum(gcd_steps(big[i], big[i + 1]) for i in range(0, 20000, 2)) / 10000
    print(f"무작위 10^18 이하 두 수 10000쌍의 평균 단계 수: {avg:.1f}")
