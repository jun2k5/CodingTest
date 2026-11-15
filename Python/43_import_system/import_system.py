"""43. 모듈과 임포트 시스템: 모듈은 한 번만 실행(sys.modules), 검색 경로, 패키지와 __init__, 상대 임포트,
__all__, 순환 임포트, importlib(import_module, reload), __name__ == '__main__'"""
import importlib
import sys
import tempfile
import textwrap
from pathlib import Path

FILES = {
    "shop/__init__.py": """
        print("  shop/__init__.py 실행")
        from .pricing import price_with_tax      # 패키지 공개 API 정리
        __all__ = ["price_with_tax"]
        VERSION = "1.0"
    """,
    "shop/pricing.py": """
        print("  shop/pricing.py 실행")
        TAX = 0.1
        def price_with_tax(p):
            return round(p * (1 + TAX))
        def _internal():
            return "비공개 관례"
    """,
    "shop/orders.py": """
        from . import pricing                    # 상대 임포트: 같은 패키지
        from .pricing import price_with_tax
        def total(items):
            return sum(price_with_tax(p) for p in items)
    """,
    "cyc_a.py": """
        import cyc_b
        A_VALUE = "a"
        def use_b():
            return cyc_b.B_VALUE                  # 함수 안에서 쓰면 안전
    """,
    "cyc_b.py": """
        import cyc_a
        B_VALUE = "b"
        try:
            EARLY = cyc_a.A_VALUE                 # 모듈 최상위에서 바로 쓰면 아직 정의 전
        except AttributeError as e:
            import re
            EARLY = "AttributeError: " + re.sub(r"from '.*?'", "from '...'", str(e))
    """,
    "counter_mod.py": """
        COUNT = 0
        COUNT += 1
    """,
}


def build(root: Path):
    for rel, src in FILES.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(src).lstrip(), encoding="utf-8")
    sys.path.insert(0, str(root))                # 검색 경로 맨 앞에 추가


def runs_once():
    print("첫 import:")
    import shop
    print("두 번째 import (출력 없음 = 다시 실행 안 됨):")
    import shop as shop_again
    print("같은 객체:", shop is shop_again, "| sys.modules에 있음:", "shop" in sys.modules, "shop.pricing" in sys.modules)
    print("패키지 공개 API:", shop.price_with_tax(1000), shop.__all__, "| 버전:", shop.VERSION)
    from shop import orders
    print("상대 임포트 모듈:", orders.total([1000, 2000]))
    ns = {}
    exec("from shop.pricing import *", ns)
    print("import * 는 밑줄 이름 제외:", "_internal" in ns, "price_with_tax" in ns)


def circular():
    import cyc_a
    import cyc_b
    print("순환 임포트 최상위 접근:", cyc_b.EARLY)
    print("함수 안에서 접근:", cyc_a.use_b())


def importlib_tools():
    mod = importlib.import_module("shop.pricing")          # 문자열로 임포트(플러그인 등)
    print("import_module:", mod.__name__, mod.TAX)
    import counter_mod
    counter_mod.COUNT = 100
    importlib.reload(counter_mod)                         # 모듈 코드를 다시 실행
    print("reload 후 COUNT:", counter_mod.COUNT)
    print("모듈 정보:", Path(mod.__file__).name, "| 패키지:", mod.__package__, "| spec 이름:", mod.__spec__.name)
    print("검색 경로 첫 항목은 방금 넣은 임시 폴더:", Path(sys.path[0]).name.startswith("tmp"))


if __name__ == "__main__":
    print("이 파일의 __name__:", __name__)
    with tempfile.TemporaryDirectory() as tmp:
        build(Path(tmp))
        runs_once()
        circular()
        importlib_tools()
        sys.path.remove(tmp)
    print("모든 검증 통과")
