"""암호와 해시: RSA(키 생성·암호화·서명), 디피-헬만 키 교환, SHA-256 직접 구현.
학습용 구현이다. 실제 서비스에는 검증된 라이브러리(cryptography, hashlib, secrets)를 쓴다."""
import hashlib, math, random, struct


# ---------- RSA ----------

def is_probable_prime(n, rng, rounds=20):
    if n < 2: return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29):
        if n % p == 0: return n == p
    d, s = n - 1, 0
    while d % 2 == 0: d //= 2; s += 1
    for _ in range(rounds):
        x = pow(rng.randrange(2, n - 1), d, n)
        if x in (1, n - 1): continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1: break
        else:
            return False
    return True


def random_prime(bits, rng):
    while True:
        p = rng.getrandbits(bits) | (3 << (bits - 2)) | 1     # 위 두 비트를 1로: p·q가 정확히 2·bits비트가 되게. 홀수 보장
        if is_probable_prime(p, rng): return p


def rsa_keygen(bits, rng, e=65537):
    """n = p·q, φ = (p-1)(q-1), d = e^(-1) mod φ. 공개 키 (n, e), 개인 키 (n, d)."""
    while True:
        p, q = random_prime(bits // 2, rng), random_prime(bits // 2, rng)
        if p == q: continue
        phi = (p - 1) * (q - 1)
        if math.gcd(e, phi) == 1:
            return (p * q, e), (p * q, pow(e, -1, phi)), (p, q)


def rsa_encrypt(m, pub):
    n, e = pub
    return pow(m, e, n)


def rsa_decrypt(c, priv):
    n, d = priv
    return pow(c, d, n)


def rsa_sign(m_hash, priv):
    return pow(m_hash, priv[1], priv[0])           # 개인 키로 "암호화"


def rsa_verify(m_hash, sig, pub):
    return pow(sig, pub[1], pub[0]) == m_hash      # 공개 키로 확인


# ---------- 디피-헬만 ----------

def diffie_hellman(p, g, rng):
    a = rng.randrange(2, p - 1)                    # 앨리스 비밀
    b = rng.randrange(2, p - 1)                    # 밥 비밀
    A, B = pow(g, a, p), pow(g, b, p)              # 공개 채널로 교환하는 값
    return A, B, pow(B, a, p), pow(A, b, p)        # 각자 계산한 공유 비밀


# ---------- SHA-256 ----------

K = [int((p ** (1 / 3) % 1) * 2 ** 32) for p in [n for n in range(2, 312) if all(n % d for d in range(2, int(n ** 0.5) + 1))][:64]]
H0 = [int((p ** 0.5 % 1) * 2 ** 32) for p in [2, 3, 5, 7, 11, 13, 17, 19]]


def rotr(x, n):
    return ((x >> n) | (x << (32 - n))) & 0xFFFFFFFF


def sha256(data: bytes) -> str:
    """1) 패딩: 1비트 + 0들 + 64비트 길이 → 512비트 배수  2) 블록마다 64라운드 압축  3) 8개 32비트 상태를 이어 붙임."""
    ml = len(data) * 8
    data += b"\x80" + b"\x00" * ((56 - (len(data) + 1) % 64) % 64) + struct.pack(">Q", ml)
    h = H0[:]
    for off in range(0, len(data), 64):
        w = list(struct.unpack(">16I", data[off:off + 64]))
        for i in range(16, 64):                    # 메시지 스케줄 확장
            s0 = rotr(w[i - 15], 7) ^ rotr(w[i - 15], 18) ^ (w[i - 15] >> 3)
            s1 = rotr(w[i - 2], 17) ^ rotr(w[i - 2], 19) ^ (w[i - 2] >> 10)
            w.append((w[i - 16] + s0 + w[i - 7] + s1) & 0xFFFFFFFF)
        a, b, c, d, e, f, g, hh = h
        for i in range(64):
            S1 = rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25)
            ch = (e & f) ^ (~e & g)
            t1 = (hh + S1 + ch + K[i] + w[i]) & 0xFFFFFFFF
            S0 = rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22)
            maj = (a & b) ^ (a & c) ^ (b & c)
            t2 = (S0 + maj) & 0xFFFFFFFF
            a, b, c, d, e, f, g, hh = (t1 + t2) & 0xFFFFFFFF, a, b, c, (d + t1) & 0xFFFFFFFF, e, f, g
        h = [(x + y) & 0xFFFFFFFF for x, y in zip(h, [a, b, c, d, e, f, g, hh])]
    return "".join(f"{x:08x}" for x in h)


if __name__ == "__main__":
    rng = random.Random(50)
    pub, priv, (p, q) = rsa_keygen(512, rng)
    print(f"RSA 512비트 키: n은 {pub[0].bit_length()}비트, e = {pub[1]}, d는 {priv[1].bit_length()}비트")
    msg = int.from_bytes("알고리즘".encode(), "big")
    c = rsa_encrypt(msg, pub)
    print("평문 '알고리즘' → 암호문 앞 20자리", str(c)[:20], "... → 복호화", rsa_decrypt(c, priv).to_bytes(12, "big").decode())
    for _ in range(300):
        m = rng.randrange(pub[0])
        assert rsa_decrypt(rsa_encrypt(m, pub), priv) == m
    h = int(sha256(b"contract v1"), 16) % pub[0]
    sig = rsa_sign(h, priv)
    print("서명 검증: 원문", rsa_verify(h, sig, pub), "/ 바뀐 문서", rsa_verify(int(sha256(b"contract v2"), 16) % pub[0], sig, pub))
    print("RSA: 무작위 300개 메시지 암호화 → 복호화 원래 값 복원")

    small_pub, small_priv, (sp, sq) = rsa_keygen(40, rng)
    n = small_pub[0]
    f = next(k for k in range(3, math.isqrt(n) + 1, 2) if n % k == 0)
    phi = (f - 1) * (n // f - 1)
    print(f"40비트 n = {n}: 시행 나눗셈으로 {f} × {n // f} 분해 → d 복원 일치 {pow(small_pub[1], -1, phi) == small_priv[1]}")

    p_dh, g_dh = 2**127 - 1, 3
    A, B, sa, sb = diffie_hellman(p_dh, g_dh, rng)
    print(f"디피-헬만 (p = 2^127-1): 공개 값 A, B 교환 후 공유 비밀 일치 {sa == sb}")

    for msg in (b"", b"abc", b"a" * 55, b"a" * 56, b"a" * 64, "알고리즘 정리".encode()):
        assert sha256(msg) == hashlib.sha256(msg).hexdigest()
    for _ in range(500):
        m = bytes(rng.randrange(256) for _ in range(rng.randint(0, 300)))
        assert sha256(m) == hashlib.sha256(m).hexdigest()
    print("SHA-256 직접 구현: 패딩 경계(55·56·64바이트) 포함 506개 입력에서 hashlib.sha256과 일치")
    print("sha256('abc') =", sha256(b"abc"))

    assert bin(ord("m") ^ ord("l")).count("1") == 1
    a, b = sha256(b"algorithm"), sha256(b"algorithl")
    diff = bin(int(a, 16) ^ int(b, 16)).count("1")
    print(f"눈사태 효과: 'algorithm'과 'algorithl'(m→l, 입력 1비트 차이)의 해시는 256비트 중 {diff}비트가 다름")
    tot = 0
    for _ in range(1000):
        m = bytearray(rng.randbytes(32)); x = sha256(bytes(m))
        m[rng.randrange(32)] ^= 1 << rng.randrange(8)
        tot += bin(int(x, 16) ^ int(sha256(bytes(m)), 16)).count("1")
    print(f"무작위 1000쌍(입력 1비트 차이) 평균: {tot / 1000:.1f}비트 다름 (이상적 값 128)")
