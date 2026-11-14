"""리포지토리, 작업 단위(Unit of Work), 서비스 레이어. 액티브 레코드와 비교한다.

python repository_uow.py 로 실행하면 무작위 검증과 예제 출력이 나온다.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
import random
import sqlite3


@dataclass
class Account:                                   # 도메인 객체: 저장 방법을 모른다
    id: int
    owner: str
    balance: int

    def withdraw(self, amount):
        if amount <= 0 or amount > self.balance:
            raise ValueError("출금 불가")
        self.balance -= amount

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("입금 불가")
        self.balance += amount


# 리포지토리: 도메인 객체 컬렉션처럼 보이는 저장소 ------------------------------------
class AccountRepository(ABC):
    @abstractmethod
    def get(self, id: int) -> Account | None: ...
    @abstractmethod
    def add(self, acc: Account) -> None: ...
    @abstractmethod
    def save(self, acc: Account) -> None: ...


class SqliteAccountRepository(AccountRepository):
    def __init__(self, conn: sqlite3.Connection): self.conn = conn

    def get(self, id):
        row = self.conn.execute("SELECT id, owner, balance FROM account WHERE id = ?", (id,)).fetchone()
        return Account(*row) if row else None

    def add(self, acc):
        self.conn.execute("INSERT INTO account VALUES (?, ?, ?)", (acc.id, acc.owner, acc.balance))

    def save(self, acc):
        self.conn.execute("UPDATE account SET balance = ? WHERE id = ?", (acc.balance, acc.id))


class InMemoryAccountRepository(AccountRepository):   # 테스트용
    def __init__(self): self.rows: dict[int, Account] = {}
    def get(self, id):
        a = self.rows.get(id)
        return Account(a.id, a.owner, a.balance) if a else None
    def add(self, acc): self.rows[acc.id] = Account(acc.id, acc.owner, acc.balance)
    def save(self, acc): self.rows[acc.id] = Account(acc.id, acc.owner, acc.balance)


# 작업 단위: 여러 변경을 하나의 트랜잭션으로 묶는다 ---------------------------------
class UnitOfWork(ABC):
    accounts: AccountRepository

    def __enter__(self): return self

    def __exit__(self, exc_type, *_):
        if exc_type:
            self.rollback()                       # 예외가 나면 전부 취소
        return False

    @abstractmethod
    def commit(self): ...
    @abstractmethod
    def rollback(self): ...


class SqliteUnitOfWork(UnitOfWork):
    def __init__(self, conn):
        self.conn = conn
        self.accounts = SqliteAccountRepository(conn)
    def commit(self): self.conn.commit()
    def rollback(self): self.conn.rollback()


class InMemoryUnitOfWork(UnitOfWork):
    def __init__(self):
        self.accounts = InMemoryAccountRepository()
        self._snapshot = {}
        self.commits = 0
    def __enter__(self):
        self._snapshot = {k: Account(v.id, v.owner, v.balance) for k, v in self.accounts.rows.items()}
        return self
    def commit(self):
        self.commits += 1
        self._snapshot = dict(self.accounts.rows)
    def rollback(self): self.accounts.rows = self._snapshot


# 서비스 레이어: 유스케이스 하나 = 함수 하나. 저장 기술을 모른다 ----------------------
def transfer(uow: UnitOfWork, src: int, dst: int, amount: int):
    if src == dst:
        raise ValueError("같은 계좌")              # get()이 매번 새 객체를 주므로 같은 계좌면 돈이 생긴다
    with uow:
        a, b = uow.accounts.get(src), uow.accounts.get(dst)
        if a is None or b is None:
            raise LookupError("계좌 없음")
        a.withdraw(amount)
        uow.accounts.save(a)                     # 출금은 반영됐지만
        b.deposit(amount)                        # 여기서 실패하면 __exit__에서 롤백
        uow.accounts.save(b)
        uow.commit()


# 비교: 액티브 레코드. 객체가 자기 저장 방법(SQL)을 직접 안다 (Django 모델 방식)
class ActiveAccount:
    conn: sqlite3.Connection

    def __init__(self, id, owner, balance): self.id, self.owner, self.balance = id, owner, balance

    @classmethod
    def get(cls, id):
        row = cls.conn.execute("SELECT id, owner, balance FROM account WHERE id = ?", (id,)).fetchone()
        return cls(*row) if row else None

    def save(self):
        self.conn.execute("UPDATE account SET balance = ? WHERE id = ?", (self.balance, self.id))
        self.conn.commit()


def make_sqlite():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE account (id INTEGER PRIMARY KEY, owner TEXT, balance INTEGER CHECK (balance >= 0))")
    return conn


def balances(uow):
    return [uow.accounts.get(i).balance for i in range(1, 4)]


if __name__ == "__main__":
    sq, mem = SqliteUnitOfWork(make_sqlite()), InMemoryUnitOfWork()
    for u in (sq, mem):
        with u:
            for i, (o, bal) in enumerate([("kim", 1000), ("lee", 500), ("park", 0)], 1):
                u.accounts.add(Account(i, o, bal))
            u.commit()

    transfer(sq, 1, 2, 300)
    print("이체 후:", balances(sq))
    assert balances(sq) == [700, 800, 0]

    for args in [(2, 3, 0), (3, 1, 50), (1, 9, 10)]:
        try:
            transfer(sq, *args)
        except (ValueError, LookupError) as e:
            print(f"transfer{args} 실패: {e} -> 잔액 {balances(sq)}")
    assert balances(sq) == [700, 800, 0]           # 실패한 이체는 흔적이 없다

    # 무작위 검증: SQLite 구현과 메모리 구현이 같은 결과를 내고, 총액이 보존된다
    transfer(mem, 1, 2, 300)
    rng = random.Random(4)
    for _ in range(2000):
        s, d, amt = rng.randint(1, 4), rng.randint(1, 3), rng.randint(-50, 600)
        r1 = r2 = "ok"
        try: transfer(sq, s, d, amt)
        except (ValueError, LookupError) as e: r1 = type(e).__name__
        try: transfer(mem, s, d, amt)
        except (ValueError, LookupError) as e: r2 = type(e).__name__
        assert r1 == r2 and balances(sq) == balances(mem) and sum(balances(sq)) == 1500
    print("무작위 이체 2000회: SQLite = 메모리 구현, 총액 1500 유지, 최종", balances(sq))

    ActiveAccount.conn = sq.conn
    a = ActiveAccount.get(1)
    a.balance += 1
    a.save()
    assert sq.accounts.get(1).balance == a.balance
    print("액티브 레코드: 객체가 save()로 스스로 저장")
    print("모든 검증 통과")
