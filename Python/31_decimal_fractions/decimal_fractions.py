"""31. decimal·fractions와 부동소수점: IEEE 754, 0.1+0.2, isclose, Decimal 생성·정밀도·반올림, Fraction"""
import math
from decimal import ROUND_DOWN, ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal, getcontext, localcontext
from fractions import Fraction


def float_basics():
    print("0.1 + 0.2:", 0.1 + 0.2, "| == 0.3:", 0.1 + 0.2 == 0.3)
    print("0.1의 실제 값:", Decimal(0.1))
    print("float.hex(0.1):", (0.1).hex(), "| as_integer_ratio:", (0.1).as_integer_ratio())
    print("isclose:", math.isclose(0.1 + 0.2, 0.3), "| 0 근처는 abs_tol 필요:",
          math.isclose(1e-12, 0.0), math.isclose(1e-12, 0.0, abs_tol=1e-9))
    print("큰 수 정밀도 손실:", 2 ** 53 + 1.0 == 2 ** 53, "| 정수는 무한 정밀도:", 2 ** 53 + 1 == 2 ** 53)
    print("round(2.675, 2):", round(2.675, 2), "| 실제 저장값:", Decimal(2.675))
    print("특수값:", float("inf") > 1e308, math.isnan(float("nan")), float("nan") == float("nan"))


def decimal_basics():
    print("문자열로 생성:", Decimal("0.1") + Decimal("0.2"), "| float로 생성:", Decimal(0.1) + Decimal(0.2))
    assert Decimal("0.1") + Decimal("0.2") == Decimal("0.3")
    print("유효 자릿수 유지:", Decimal("1.10") + Decimal("2.20"), "| 곱:", Decimal("1.10") * 3)
    print("기본 정밀도:", getcontext().prec, "자리 | 1/3:", Decimal(1) / Decimal(3))
    with localcontext() as ctx:
        ctx.prec = 5
        print("localcontext prec=5:", Decimal(1) / Decimal(7))
    print("밖에서는 원래대로:", Decimal(1) / Decimal(7))


def rounding():
    values = [Decimal("2.5"), Decimal("3.5"), Decimal("2.675"), Decimal("-2.5")]
    cent = Decimal("0.01")
    print("HALF_EVEN(은행원, 기본):", [v.quantize(Decimal("1"), rounding=ROUND_HALF_EVEN) for v in values[:2]])
    print("HALF_UP(학교식):", [v.quantize(Decimal("1"), rounding=ROUND_HALF_UP) for v in values[:2]])
    print("2.675 → 소수 둘째(HALF_UP):", values[2].quantize(cent, rounding=ROUND_HALF_UP))
    print("-2.5 HALF_UP:", values[3].quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    print("절사(ROUND_DOWN):", Decimal("19.999").quantize(cent, rounding=ROUND_DOWN))
    assert values[2].quantize(cent, rounding=ROUND_HALF_UP) == Decimal("2.68")


def money_split():
    total = Decimal("100.00")
    n = 3
    each = (total / n).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
    shares = [each] * n
    shares[0] += total - sum(shares)            # 남는 1원(센트)을 첫 사람에게
    print("100.00을 3명:", shares, "| 합계:", sum(shares))
    assert sum(shares) == total


def fractions_demo():
    a = Fraction(1, 3)
    print("Fraction:", a + Fraction(1, 6), a * 3, "| 문자열:", Fraction("0.25"))
    print("float를 Fraction으로(정확한 이진값):", Fraction(0.1))
    print("limit_denominator:", Fraction(0.1).limit_denominator(1000))
    total = sum(Fraction(1, n) for n in range(1, 6))
    print("1+1/2+...+1/5:", total, "≈", float(total))
    assert Fraction(1, 3) * 3 == 1


def performance_note():
    import timeit
    t_float = timeit.timeit("a * b + a", setup="a, b = 1.1, 2.2", number=200_000)
    t_dec = timeit.timeit("a * b + a", setup="from decimal import Decimal; a, b = Decimal('1.1'), Decimal('2.2')", number=200_000)
    t_frac = timeit.timeit("a * b + a", setup="from fractions import Fraction; a, b = Fraction(11, 10), Fraction(22, 10)", number=200_000)
    print(f"20만 번 a*b+a - float: {t_float * 1000:.0f}ms, Decimal: {t_dec * 1000:.0f}ms, Fraction: {t_frac * 1000:.0f}ms")


if __name__ == "__main__":
    float_basics()
    decimal_basics()
    rounding()
    money_split()
    fractions_demo()
    performance_note()
    print("모든 검증 통과")
