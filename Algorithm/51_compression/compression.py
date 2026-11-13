"""무손실 압축: 런 길이 부호화(RLE), 허프만 코딩(부호화·복호화), LZ77. zlib(DEFLATE = LZ77 + 허프만)과 비교."""
import heapq, random, zlib
from collections import Counter


def rle_encode(data: bytes):
    out, i = [], 0
    while i < len(data):
        j = i
        while j < len(data) and data[j] == data[i] and j - i < 255: j += 1
        out.append((j - i, data[i])); i = j
    return out


def rle_decode(pairs):
    return b"".join(bytes([v]) * n for n, v in pairs)


def huffman_codes(data: bytes):
    freq = Counter(data)
    if len(freq) == 1:
        return {next(iter(freq)): "0"}
    heap = [(f, i, sym) for i, (sym, f) in enumerate(sorted(freq.items()))]
    heapq.heapify(heap)
    cnt = len(heap)
    while len(heap) > 1:
        f1, _, a = heapq.heappop(heap)
        f2, _, b = heapq.heappop(heap)
        heapq.heappush(heap, (f1 + f2, cnt, (a, b))); cnt += 1
    codes = {}
    stack = [(heap[0][2], "")]
    while stack:
        node, code = stack.pop()
        if isinstance(node, tuple):
            stack.append((node[0], code + "0")); stack.append((node[1], code + "1"))
        else:
            codes[node] = code
    return codes


def huffman_encode(data: bytes):
    codes = huffman_codes(data) if data else {}
    bits = "".join(codes[b] for b in data)
    return codes, bits


def huffman_decode(codes, bits):
    """접두사 코드라 앞에서부터 읽다가 코드표에 있는 비트열이 되는 순간 그 문자로 확정할 수 있다."""
    rev = {v: k for k, v in codes.items()}
    out, cur = bytearray(), ""
    for b in bits:
        cur += b
        if cur in rev:
            out.append(rev[cur]); cur = ""
    return bytes(out)


def lz77_encode(data: bytes, window=4096, max_len=255, min_len=3):
    """(거리, 길이, 다음 바이트) 토큰. 앞에서 본 window 안에서 가장 긴 일치를 찾는다.
    일치가 min_len보다 짧으면 (0, 0, 바이트) 리터럴. 해시로 후보 위치를 모아 탐색을 줄인다."""
    out, i, n = [], 0, len(data)
    pos = {}                                       # 3바이트 → 그 3바이트가 시작한 위치들
    while i < n:
        best_len, best_dist = 0, 0
        if i + min_len <= n:
            for j in reversed(pos.get(data[i:i + min_len], [])[-64:]):
                if i - j > window: break
                k = 0
                while k < max_len and i + k < n - 1 and data[j + k] == data[i + k]:
                    k += 1                         # j + k가 i를 넘어가도 된다(겹치는 복사)
                if k > best_len: best_len, best_dist = k, i - j
        if best_len >= min_len:
            nxt = data[i + best_len]
            out.append((best_dist, best_len, nxt))
            step = best_len + 1
        else:
            out.append((0, 0, data[i])); step = 1
        for t in range(i, min(i + step, n - min_len + 1)):
            pos.setdefault(data[t:t + min_len], []).append(t)
        i += step
    return out


def lz77_decode(tokens):
    out = bytearray()
    for dist, length, nxt in tokens:
        start = len(out) - dist
        for k in range(length):                   # 한 바이트씩 복사해야 겹치는 일치(dist < length)도 맞다
            out.append(out[start + k])
        out.append(nxt)
    return bytes(out)


def lz77_size_bits(tokens):
    """토큰 크기 추정: 리터럴 = 플래그 1 + 8비트, 일치 = 플래그 1 + 거리 12 + 길이 8 + 다음 바이트 8."""
    return sum(9 if d == 0 else 29 for d, l, c in tokens)


def sample_text(rng, n_words):
    words = ("the of and to in is that for it as with was on be by this are or algorithm data structure "
             "tree graph sort search hash table node edge path cost time space memory").split()
    return " ".join(rng.choice(words) for _ in range(n_words)).encode()


if __name__ == "__main__":
    rng = random.Random(51)
    for _ in range(500):
        kind = rng.randrange(3)
        if kind == 0: d = bytes(rng.randrange(256) for _ in range(rng.randint(0, 200)))
        elif kind == 1: d = bytes(rng.choice(b"ab") for _ in range(rng.randint(0, 200)))
        else: d = sample_text(rng, rng.randint(0, 60))
        assert rle_decode(rle_encode(d)) == d
        codes, bits = huffman_encode(d)
        assert huffman_decode(codes, bits) == d
        assert lz77_decode(lz77_encode(d)) == d
        assert all(not b.startswith(a) for a in codes.values() for b in codes.values() if a != b)
    print("RLE·허프만·LZ77: 500개 입력(무작위, 2글자, 영어 단어)에서 압축 → 복원이 원본과 같음, 허프만 코드는 접두사 코드")

    t = b"ABABABABABAB"
    print("LZ77('ABABABABABAB') 토큰:", lz77_encode(t), "→ 겹치는 복사(거리 2, 길이 9)로 한 번에 표현")
    codes, bits = huffman_encode(b"abracadabra")
    print("허프만('abracadabra') 코드:", {chr(k): v for k, v in sorted(codes.items())}, f"→ {len(bits)}비트 (고정 8비트면 88비트)")
    print("RLE(b'aaaabbbcca') =", [(n, chr(v)) for n, v in rle_encode(b"aaaabbbcca")])

    print()
    tests = {
        "영어 단어 텍스트": sample_text(rng, 20000),
        "같은 바이트 반복": b"A" * 50000 + b"B" * 50000,
        "무작위 바이트": bytes(rng.randrange(256) for _ in range(100000)),
        "무작위 4글자(ACGT)": bytes(rng.choice(b"ACGT") for _ in range(100000)),
    }
    print(f"{'입력':16s} {'원본':>8s} {'RLE':>8s} {'허프만':>8s} {'LZ77':>8s} {'LZ77+허프만':>11s} {'zlib -9':>8s}  (바이트)")
    for name, d in tests.items():
        rle = len(rle_encode(d)) * 2
        _, bits = huffman_encode(d)
        huff = (len(bits) + 7) // 8
        tok = lz77_encode(d)
        lz = (lz77_size_bits(tok) + 7) // 8
        # LZ77 토큰을 바이트열로 펼친 뒤 허프만: DEFLATE의 단순화 버전
        flat = bytes(x for dt, ln, c in tok for x in ((c,) if dt == 0 else (dt >> 8, dt & 255, ln, c)))
        _, b2 = huffman_encode(flat)
        lzh = (len(b2) + 7) // 8 + len(tok) // 8  # 토큰 종류 플래그 1비트씩
        z = len(zlib.compress(d, 9))
        print(f"{name:16s} {len(d):8,d} {rle:8,d} {huff:8,d} {lz:8,d} {lzh:11,d} {z:8,d}")
