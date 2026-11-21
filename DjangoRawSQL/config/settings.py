"""로컬 실험용 설정. ORM 모델은 쓰지 않고 DB 연결 설정만 Django에 맡긴다."""
import os

SECRET_KEY = "local-dev-only"
DEBUG = True
ALLOWED_HOSTS = ["*"]
ROOT_URLCONF = "config.urls"
USE_TZ = True
TIME_ZONE = "Asia/Seoul"

INSTALLED_APPS = ["rest_framework", "api"]
MIDDLEWARE = []

DB = {
    "NAME": os.environ.get("DB_NAME", "shop"),
    "USER": os.environ.get("DB_USER", "shop"),
    "PASSWORD": os.environ.get("DB_PASSWORD", "shop"),
    "HOST": os.environ.get("DB_HOST", "localhost"),
    "PORT": os.environ.get("DB_PORT", "54329"),
}

# 방식 A: Django가 관리하는 연결(connection.cursor())
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        **DB,
        "CONN_MAX_AGE": 0,
    },
    # 09편 비교용: Django 5.1+ 내장 연결 풀(psycopg_pool 사용). CONN_MAX_AGE는 0이어야 한다.
    "pooled": {
        "ENGINE": "django.db.backends.postgresql",
        **DB,
        "CONN_MAX_AGE": 0,
        "OPTIONS": {"pool": {"min_size": 1, "max_size": 4, "timeout": 2}},
    },
    # 09편 비교용: 연결마다 기본 타임아웃을 건다(libpq options).
    "tuned": {
        "ENGINE": "django.db.backends.postgresql",
        **DB,
        "OPTIONS": {
            "options": "-c lock_timeout=2s -c statement_timeout=5s "
                       "-c idle_in_transaction_session_timeout=10s"
        },
    },
}

# 방식 B: psycopg_pool이 관리하는 연결
SHOP_B_POOL = {"min_size": 1, "max_size": 5, "timeout": 5.0}

# 어느 방식으로 DB에 접근할지: "a" 또는 "b"
SHOP_DB_BACKEND = os.environ.get("SHOP_DB_BACKEND", "a")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": [],
    "UNAUTHENTICATED_USER": None,
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
}
