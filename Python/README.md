# Python

velog 시리즈 [파이썬 심화](https://velog.io/@jun2k5/python-00-series-intro)의 예제 코드다.

- 기준 버전: Python 3.14 (표준 라이브러리만)
- 폴더마다 `python 파일명.py`로 실행하면 `assert` 기반 검증과 예제 출력이 나오고, 마지막 줄에 `모든 검증 통과`가 출력된다.
- `30_datetime_zoneinfo`는 Windows에서 시간대 데이터 패키지가 필요하다: `pip install tzdata`

| # | 폴더 | 주제 | 글 |
|---|---|---|---|
| 01 | [01_object_model](01_object_model) | 객체 모델: 이름과 객체, 가변·불변, 복사 | [글](https://velog.io/@jun2k5/python-01-object-model) |
| 02 | [02_int_str_internals](02_int_str_internals) | 정수와 문자열 내부 | [글](https://velog.io/@jun2k5/python-02-int-str-internals) |
| 03 | [03_scope_closure](03_scope_closure) | 스코프와 클로저 | [글](https://velog.io/@jun2k5/python-03-scope-closure) |
| 04 | [04_function_args](04_function_args) | 함수 인자 심화 | [글](https://velog.io/@jun2k5/python-04-function-args) |
| 05 | [05_unpacking_comprehension](05_unpacking_comprehension) | 언패킹, 컴프리헨션, 왈러스 연산자 | [글](https://velog.io/@jun2k5/python-05-unpacking-comprehension) |
| 06 | [06_collections_internals](06_collections_internals) | list·dict·set 내부 구조와 시간복잡도 | [글](https://velog.io/@jun2k5/python-06-collections-internals) |
| 07 | [07_iterator_generator](07_iterator_generator) | 이터레이터와 제너레이터 | [글](https://velog.io/@jun2k5/python-07-iterator-generator) |
| 08 | [08_decorator](08_decorator) | 데코레이터 원리 | [글](https://velog.io/@jun2k5/python-08-decorator) |
| 09 | [09_exceptions](09_exceptions) | 예외 심화 | [글](https://velog.io/@jun2k5/python-09-exceptions) |
| 10 | [10_builtins](10_builtins) | 내장 함수 심화 | [글](https://velog.io/@jun2k5/python-10-builtins) |
| 11 | [11_defaultdict](11_defaultdict) | defaultdict | [글](https://velog.io/@jun2k5/python-11-defaultdict) |
| 12 | [12_counter](12_counter) | Counter | [글](https://velog.io/@jun2k5/python-12-counter) |
| 13 | [13_deque](13_deque) | deque | [글](https://velog.io/@jun2k5/python-13-deque) |
| 14 | [14_ordereddict_chainmap](14_ordereddict_chainmap) | OrderedDict와 ChainMap | [글](https://velog.io/@jun2k5/python-14-ordereddict-chainmap) |
| 15 | [15_record_types](15_record_types) | 레코드 타입 비교: namedtuple, dataclass, TypedDict | [글](https://velog.io/@jun2k5/python-15-record-types) |
| 16 | [16_dataclasses](16_dataclasses) | dataclasses 심화 | [글](https://velog.io/@jun2k5/python-16-dataclasses) |
| 17 | [17_heapq](17_heapq) | heapq 심화 | [글](https://velog.io/@jun2k5/python-17-heapq) |
| 18 | [18_bisect](18_bisect) | bisect 심화 | [글](https://velog.io/@jun2k5/python-18-bisect) |
| 19 | [19_itertools_tools](19_itertools_tools) | itertools ① 이터레이터 도구 | [글](https://velog.io/@jun2k5/python-19-itertools-tools) |
| 20 | [20_itertools_combinatorics](20_itertools_combinatorics) | itertools ② 조합과 레시피 | [글](https://velog.io/@jun2k5/python-20-itertools-combinatorics) |
| 21 | [21_functools_cache](21_functools_cache) | functools ① 캐시 | [글](https://velog.io/@jun2k5/python-21-functools-cache) |
| 22 | [22_functools_tools](22_functools_tools) | functools ② 함수 도구 | [글](https://velog.io/@jun2k5/python-22-functools-tools) |
| 23 | [23_operator](23_operator) | operator 모듈 | [글](https://velog.io/@jun2k5/python-23-operator) |
| 24 | [24_contextlib](24_contextlib) | contextlib | [글](https://velog.io/@jun2k5/python-24-contextlib) |
| 25 | [25_enum](25_enum) | enum 심화 | [글](https://velog.io/@jun2k5/python-25-enum) |
| 26 | [26_typing](26_typing) | typing 심화 | [글](https://velog.io/@jun2k5/python-26-typing) |
| 27 | [27_re](27_re) | re 정규식 심화 | [글](https://velog.io/@jun2k5/python-27-re) |
| 28 | [28_pathlib](28_pathlib) | pathlib·shutil·tempfile | [글](https://velog.io/@jun2k5/python-28-pathlib) |
| 29 | [29_serialization](29_serialization) | json·pickle·csv | [글](https://velog.io/@jun2k5/python-29-serialization) |
| 30 | [30_datetime_zoneinfo](30_datetime_zoneinfo) | datetime·zoneinfo | [글](https://velog.io/@jun2k5/python-30-datetime-zoneinfo) |
| 31 | [31_decimal_fractions](31_decimal_fractions) | 부동소수점과 decimal·fractions | [글](https://velog.io/@jun2k5/python-31-decimal-fractions) |
| 32 | [32_logging](32_logging) | logging 심화 | [글](https://velog.io/@jun2k5/python-32-logging) |
| 33 | [33_unittest_mock](33_unittest_mock) | unittest.mock | [글](https://velog.io/@jun2k5/python-33-unittest-mock) |
| 34 | [34_profiling](34_profiling) | 성능 측정: timeit, cProfile, tracemalloc | [글](https://velog.io/@jun2k5/python-34-profiling) |
| 35 | [35_threads_processes](35_threads_processes) | 스레드와 프로세스 | [글](https://velog.io/@jun2k5/python-35-threads-processes) |
| 36 | [36_asyncio](36_asyncio) | asyncio | [글](https://velog.io/@jun2k5/python-36-asyncio) |
| 37 | [37_pattern_matching](37_pattern_matching) | 구조적 패턴 매칭 | [글](https://velog.io/@jun2k5/python-37-pattern-matching) |
| 38 | [38_data_model](38_data_model) | 데이터 모델과 매직 메서드 | [글](https://velog.io/@jun2k5/python-38-data-model) |
| 39 | [39_descriptors](39_descriptors) | 디스크립터와 property | [글](https://velog.io/@jun2k5/python-39-descriptors) |
| 40 | [40_attribute_lookup](40_attribute_lookup) | 속성 조회 순서와 `__slots__` | [글](https://velog.io/@jun2k5/python-40-attribute-lookup) |
| 41 | [41_mro_super](41_mro_super) | MRO와 super() | [글](https://velog.io/@jun2k5/python-41-mro-super) |
| 42 | [42_metaclass](42_metaclass) | 클래스 생성과 메타클래스 | [글](https://velog.io/@jun2k5/python-42-metaclass) |
| 43 | [43_import_system](43_import_system) | 모듈과 임포트 시스템 | [글](https://velog.io/@jun2k5/python-43-import-system) |
| 44 | [44_memory](44_memory) | 메모리 관리 | [글](https://velog.io/@jun2k5/python-44-memory) |
| 45 | [45_bytecode_gil](45_bytecode_gil) | 바이트코드와 GIL | [글](https://velog.io/@jun2k5/python-45-bytecode-gil) |

46번 [고급 파이썬 체크리스트와 상황별 도구 선택표](https://velog.io/@jun2k5/python-46-checklist)는 시리즈 정리 글이라 코드가 없다.
