"""빌더 패턴: 복잡한 객체를 단계별로 만들고, 만드는 과정과 결과 표현을 분리한다.

python builder.py 로 실행하면 검증과 예제 출력이 나온다.
"""
from dataclasses import dataclass, field


@dataclass(frozen=True)                    # 완성된 객체는 불변
class HttpRequest:
    method: str
    url: str
    headers: tuple = ()
    params: tuple = ()
    body: str | None = None
    timeout: float = 10.0
    retries: int = 0


class HttpRequestBuilder:
    def __init__(self, url: str):
        self._url = url
        self._method = "GET"
        self._headers: dict[str, str] = {}
        self._params: dict[str, str] = {}
        self._body = None
        self._timeout = 10.0
        self._retries = 0

    def method(self, m: str):
        self._method = m.upper()
        return self                        # 자기 자신을 돌려줘 메서드 체이닝

    def header(self, k: str, v: str):
        self._headers[k] = v
        return self

    def param(self, k: str, v):
        self._params[k] = str(v)
        return self

    def json(self, text: str):
        self._body = text
        self._headers["Content-Type"] = "application/json"
        return self

    def timeout(self, sec: float):
        self._timeout = sec
        return self

    def retries(self, n: int):
        self._retries = n
        return self

    def build(self) -> HttpRequest:        # 검증은 마지막에 한 번에
        if self._method in ("GET", "DELETE") and self._body is not None:
            raise ValueError(f"{self._method} 요청에는 body를 넣지 않는다")
        if self._timeout <= 0:
            raise ValueError("timeout은 양수")
        if not self._url.startswith(("http://", "https://")):
            raise ValueError("http(s) URL만 허용")
        return HttpRequest(
            self._method, self._url,
            tuple(sorted(self._headers.items())),
            tuple(sorted(self._params.items())),
            self._body, self._timeout, self._retries,
        )


# 디렉터: 자주 쓰는 조립 순서를 이름 붙여 재사용
class RequestDirector:
    @staticmethod
    def api_get(url: str, token: str) -> HttpRequest:
        return (HttpRequestBuilder(url)
                .header("Authorization", f"Bearer {token}")
                .header("Accept", "application/json")
                .timeout(3).retries(2)
                .build())


# 비교: 점층적 생성자 (telescoping constructor)
class TelescopingRequest:
    def __init__(self, method, url, headers=None, params=None, body=None, timeout=10.0, retries=0):
        self.args = (method, url, headers, params, body, timeout, retries)


if __name__ == "__main__":
    req = (HttpRequestBuilder("https://api.example.com/users")
           .method("post")
           .header("X-Trace", "abc")
           .json('{"name": "kim"}')
           .timeout(5)
           .build())
    print(req)
    assert req.method == "POST" and ("Content-Type", "application/json") in req.headers

    r2 = RequestDirector.api_get("https://api.example.com/me", "t0k")
    print(r2)
    assert r2.retries == 2 and r2.timeout == 3

    for bad in [lambda: HttpRequestBuilder("https://x").json("{}").build(),
                lambda: HttpRequestBuilder("https://x").timeout(0).build(),
                lambda: HttpRequestBuilder("ftp://x").build()]:
        try:
            bad()
            raise AssertionError
        except ValueError as e:
            print("검증 실패:", e)

    try:
        req.timeout = 1                    # frozen dataclass라 바꿀 수 없다
        raise AssertionError
    except AttributeError:
        pass

    # 순서만으로 의미를 알기 어려운 점층적 생성자
    t = TelescopingRequest("GET", "https://x", None, None, None, 3, 2)
    print("점층적 생성자 호출: TelescopingRequest('GET', 'https://x', None, None, None, 3, 2)")
    print("모든 검증 통과")
