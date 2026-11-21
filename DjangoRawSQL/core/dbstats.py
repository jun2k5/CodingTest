"""06편: 남의 DB에서 인덱스 요청 근거를 모으는 조회. 읽기 권한만 있으면 된다."""
from core.db import get_db

TOP_STATEMENTS = """
SELECT calls, rows,
       round((shared_blks_hit + shared_blks_read)::numeric / calls) AS blocks_per_call,
       left(regexp_replace(query, '\s+', ' ', 'g'), 80) AS query
FROM pg_stat_statements
WHERE dbid = (SELECT oid FROM pg_database WHERE datname = current_database())
  AND query NOT ILIKE '%%pg_stat%%'
ORDER BY shared_blks_hit + shared_blks_read DESC
LIMIT %(limit)s
"""

TABLE_SCANS = """
SELECT relname, seq_scan, seq_tup_read, idx_scan
FROM pg_stat_user_tables
WHERE relname = ANY(%(tables)s)
ORDER BY relname
"""

INDEX_USAGE = """
SELECT indexrelname, idx_scan
FROM pg_stat_user_indexes
WHERE relname = %(table)s
ORDER BY indexrelname
"""

EXISTING_INDEXES = """
SELECT indexname, indexdef FROM pg_indexes WHERE tablename = %(table)s ORDER BY indexname
"""


def top_statements(limit: int = 5) -> list[dict]:
    return get_db().fetch_all(TOP_STATEMENTS, {"limit": limit})


def table_scans(tables: list[str]) -> list[dict]:
    return get_db().fetch_all(TABLE_SCANS, {"tables": tables})


def index_usage(table: str) -> list[dict]:
    return get_db().fetch_all(INDEX_USAGE, {"table": table})


def existing_indexes(table: str) -> list[dict]:
    return get_db().fetch_all(EXISTING_INDEXES, {"table": table})
