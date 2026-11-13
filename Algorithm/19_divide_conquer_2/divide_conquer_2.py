"""분할 정복 ②: 카라츠바 곱셈과 슈트라센 행렬 곱셈."""
import random


MUL = [0]


def karatsuba(x, y):
    """큰 정수 곱셈. 곱셈 4번 대신 3번으로 나눠 O(n^1.585)."""
    if x < 10 or y < 10:
        MUL[0] += 1
        return x * y
    m = max(len(str(x)), len(str(y))) // 2
    p = 10 ** m
    a, b = divmod(x, p)                       # x = a·10^m + b
    c, d = divmod(y, p)                       # y = c·10^m + d
    ac = karatsuba(a, c)
    bd = karatsuba(b, d)
    mid = karatsuba(a + b, c + d) - ac - bd    # ad + bc 를 곱셈 1번으로
    return ac * p * p + mid * p + bd


def schoolbook_digit_mults(x, y):
    """학교식 곱셈의 한 자리 곱셈 횟수 = 자릿수 곱."""
    return len(str(x)) * len(str(y))


def mat_add(A, B, sign=1):
    return [[a + sign * b for a, b in zip(ra, rb)] for ra, rb in zip(A, B)]


def mat_mul_naive(A, B):
    n, m, p = len(A), len(B), len(B[0])
    return [[sum(A[i][k] * B[k][j] for k in range(m)) for j in range(p)] for i in range(n)]


def strassen(A, B):
    """n이 2의 거듭제곱인 정사각 행렬. 부분 곱 8번 대신 7번으로 O(n^2.807)."""
    n = len(A)
    if n <= 2:
        return mat_mul_naive(A, B)
    h = n // 2
    split = lambda M: ([r[:h] for r in M[:h]], [r[h:] for r in M[:h]], [r[:h] for r in M[h:]], [r[h:] for r in M[h:]])
    A11, A12, A21, A22 = split(A)
    B11, B12, B21, B22 = split(B)
    M1 = strassen(mat_add(A11, A22), mat_add(B11, B22))
    M2 = strassen(mat_add(A21, A22), B11)
    M3 = strassen(A11, mat_add(B12, B22, -1))
    M4 = strassen(A22, mat_add(B21, B11, -1))
    M5 = strassen(mat_add(A11, A12), B22)
    M6 = strassen(mat_add(A21, A11, -1), mat_add(B11, B12))
    M7 = strassen(mat_add(A12, A22, -1), mat_add(B21, B22))
    C11 = mat_add(mat_add(M1, M4), mat_add(M7, M5, -1))
    C12 = mat_add(M3, M5)
    C21 = mat_add(M2, M4)
    C22 = mat_add(mat_add(M1, M2, -1), mat_add(M3, M6))
    return [r1 + r2 for r1, r2 in zip(C11, C12)] + [r1 + r2 for r1, r2 in zip(C21, C22)]


if __name__ == "__main__":
    rng = random.Random(61)
    for _ in range(500):
        x, y = rng.randint(0, 10 ** rng.randint(1, 60)), rng.randint(0, 10 ** rng.randint(1, 60))
        assert karatsuba(x, y) == x * y
    print("카라츠바: 500개 입력에서 x*y와 일치")
    for digits in (64, 256, 1024):
        x, y = rng.randint(10 ** (digits - 1), 10 ** digits - 1), rng.randint(10 ** (digits - 1), 10 ** digits - 1)
        MUL[0] = 0; karatsuba(x, y)
        print(f"{digits}자리 × {digits}자리: 학교식 한 자리 곱 {schoolbook_digit_mults(x, y):,}번, 카라츠바 기본 곱 {MUL[0]:,}번")

    for n in (1, 2, 4, 8, 16):
        for _ in range(20):
            A = [[rng.randint(-9, 9) for _ in range(n)] for _ in range(n)]
            B = [[rng.randint(-9, 9) for _ in range(n)] for _ in range(n)]
            assert strassen(A, B) == mat_mul_naive(A, B)
    print("슈트라센: n=1,2,4,8,16 각 20개 행렬에서 일반 곱셈과 일치")
    for k in range(1, 7):
        n = 2 ** k
        print(f"n={n:3d}: 일반 곱셈 원소 곱 {n**3:,}번, 슈트라센(끝까지 분할 시) {7**k:,}번")
