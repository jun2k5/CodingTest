"""27. re 정규식 심화: match/search/fullmatch, 그룹과 이름 그룹, 탐욕·게으른 매칭, 전후방 탐색, finditer, sub 함수, 플래그, 컴파일"""
import re

LOG = """2026-11-15 09:12:01 ERROR [db] timeout after 30s
2026-11-15 09:12:05 INFO  [web] GET /users 200
2026-11-15 09:13:40 ERROR [web] GET /orders 500"""


def match_search_fullmatch():
    s = "order-2026"
    print("match(문자열 시작에서만):", bool(re.match(r"\d+", s)))
    print("search(어디서든):", re.search(r"\d+", s).group())
    print("fullmatch(전체가 일치):", bool(re.fullmatch(r"[a-z]+-\d{4}", s)), bool(re.fullmatch(r"\d{4}", s)))


def groups():
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", LOG)
    print("번호 그룹:", m.group(0), m.group(1), m.groups())
    pattern = re.compile(r"(?P<time>\d{2}:\d{2}:\d{2}) (?P<level>ERROR|INFO)\s+\[(?P<mod>\w+)\]")
    first = pattern.search(LOG)
    print("이름 그룹:", first["level"], first.group("mod"), first.groupdict())
    print("비캡처 그룹 (?:):", re.findall(r"(?:GET|POST) (/\w+)", LOG))


def finditer_and_findall():
    pattern = re.compile(r"(?P<level>ERROR) \[(?P<mod>\w+)\] (?P<msg>.+)")
    errors = [m.groupdict() for m in pattern.finditer(LOG)]
    print("finditer로 레코드:", errors)
    print("findall(그룹 2개 → 튜플):", re.findall(r"\[(\w+)\].*?(\d{3})$", LOG, flags=re.M))


def greedy_lazy():
    html = '<b>bold</b> and <i>italic</i>'
    print("탐욕적 .*:", re.findall(r"<.*>", html))
    print("게으른 .*?:", re.findall(r"<.*?>", html))
    print("부정 문자 클래스 [^>]*:", re.findall(r"<[^>]*>", html))


def lookaround():
    prices = "KRW1000 USD20 KRW350"
    print("전방 탐색(?=):", re.findall(r"\d+(?=\s|$)", prices))
    print("후방 탐색(?<=KRW):", re.findall(r"(?<=KRW)\d+", prices))
    print("부정 후방(?<!KRW):", re.findall(r"(?<!KRW)(?<!\d)\d+", prices))
    pw_ok = re.compile(r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$")
    print("비밀번호 규칙(전방 탐색 여러 개):", [bool(pw_ok.match(p)) for p in ["abcdefgh", "Abcdefg1", "Ab1"]])


def substitution():
    print("sub 역참조:", re.sub(r"(\d{4})-(\d{2})-(\d{2})", r"\3/\2/\1", "2026-11-15"))
    print("이름 그룹 역참조:", re.sub(r"(?P<y>\d{4})-(?P<m>\d{2})", r"\g<m>월 \g<y>년", "2026-11"))

    def mask(m):
        return m.group()[:3] + "*" * (len(m.group()) - 3)
    print("함수로 치환:", re.sub(r"\b\w+@\w+\.\w+\b", mask, "연락처 kim@test.com"))
    print("subn(개수):", re.subn(r"\s+", " ", "a   b \t c"))
    print("split 구분자 여러 개:", re.split(r"\s*[,;]\s*", "a, b;c ,d"))


def flags_and_verbose():
    print("IGNORECASE:", re.findall(r"error", LOG, flags=re.I)[:2])
    print("MULTILINE ^:", re.findall(r"^\S+ (\S+)", LOG, flags=re.M))
    phone = re.compile(r"""
        (?P<area>0\d{1,2})   # 지역번호
        [-.\s]?
        (?P<mid>\d{3,4})     # 국번
        [-.\s]?
        (?P<last>\d{4})      # 번호
    """, re.VERBOSE)
    print("VERBOSE:", phone.fullmatch("02-1234-5678").groupdict())
    print("escape:", re.escape("1+1=2?"))


def unicode_word():
    text = "파이썬3 python_3"
    print("\\w는 유니코드(한글 포함):", re.findall(r"\w+", text))
    print("ASCII 플래그:", re.findall(r"\w+", text, flags=re.A))


if __name__ == "__main__":
    match_search_fullmatch()
    groups()
    finditer_and_findall()
    greedy_lazy()
    lookaround()
    substitution()
    flags_and_verbose()
    unicode_word()
    assert re.sub(r"(\d{4})-(\d{2})-(\d{2})", r"\3/\2/\1", "2026-11-15") == "15/11/2026"
    print("모든 검증 통과")
