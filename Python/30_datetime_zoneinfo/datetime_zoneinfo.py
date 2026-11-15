"""30. datetime·zoneinfo: naive와 aware, UTC 저장, 시간대 변환, 일광절약시간, timedelta, 파싱·포맷"""
from datetime import UTC, date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

SEOUL = ZoneInfo("Asia/Seoul")
NY = ZoneInfo("America/New_York")


def naive_vs_aware():
    naive = datetime(2026, 11, 15, 9, 0)
    aware = datetime(2026, 11, 15, 9, 0, tzinfo=SEOUL)
    print("naive tzinfo:", naive.tzinfo, "| aware:", aware.tzinfo, aware.utcoffset())
    try:
        naive < aware
    except TypeError as e:
        print("naive와 aware 비교 불가:", e)
    print("utcnow 대신 now(UTC):", datetime.now(UTC).tzinfo)


def conversion():
    meeting = datetime(2026, 11, 15, 9, 0, tzinfo=SEOUL)
    print("서울 9시 = 뉴욕:", meeting.astimezone(NY), "| UTC:", meeting.astimezone(UTC))
    as_utc = meeting.astimezone(UTC)
    print("같은 순간이라 같다:", meeting == as_utc, "| 표시만 다름")
    stored = as_utc.isoformat()
    print("UTC ISO 저장 문자열:", stored)
    back = datetime.fromisoformat(stored).astimezone(SEOUL)
    print("읽어서 서울로:", back)
    assert back == meeting


def replace_vs_astimezone():
    naive = datetime(2026, 11, 15, 9, 0)
    wrong = naive.replace(tzinfo=NY)          # 시각은 그대로 두고 꼬리표만 붙임
    right = naive.replace(tzinfo=SEOUL).astimezone(NY)
    print("replace(tzinfo=):", wrong, "| astimezone:", right)
    print("같은 순간인가:", wrong == right)


def dst():
    before = datetime(2026, 3, 7, 12, 0, tzinfo=NY)
    after = before + timedelta(days=1)
    print("뉴욕 DST 시작 전후 오프셋:", before.utcoffset(), "→", after.utcoffset())
    real = after.astimezone(UTC) - before.astimezone(UTC)
    print("벽시계 하루(+1 day)의 실제 경과:", real)
    assert real == timedelta(hours=23)

    ambiguous = datetime(2026, 11, 1, 1, 30, tzinfo=NY)
    print("가을 1:30 (fold=0, 1):", ambiguous.utcoffset(), ambiguous.replace(fold=1).utcoffset())


def arithmetic():
    d1, d2 = date(2026, 1, 1), date(2026, 11, 15)
    print("날짜 차이:", (d2 - d1).days, "일")
    td = timedelta(days=1, hours=2, minutes=30)
    print("timedelta:", td, "| 총 초:", td.total_seconds())
    print("요일(월=0):", d2.weekday(), "| ISO 주차:", d2.isocalendar().week)
    month_end = (date(2026, 2, 1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    print("2월 말일:", month_end)


def parse_format():
    dt = datetime.strptime("2026/11/15 21:05", "%Y/%m/%d %H:%M").replace(tzinfo=SEOUL)
    print("strptime:", dt)
    print("strftime:", dt.strftime("%Y년 %m월 %d일 %H시 %M분 (%a)"))
    print("isoformat:", dt.isoformat(timespec="minutes"))
    print("fromisoformat Z(3.11+):", datetime.fromisoformat("2026-11-15T12:00:00Z"))
    print("timestamp(유닉스 초):", int(dt.timestamp()), "| 역변환:", datetime.fromtimestamp(dt.timestamp(), tz=UTC))
    print("고정 오프셋:", datetime(2026, 1, 1, tzinfo=timezone(timedelta(hours=9))))


if __name__ == "__main__":
    naive_vs_aware()
    conversion()
    replace_vs_astimezone()
    dst()
    arithmetic()
    parse_format()
    print("모든 검증 통과")
