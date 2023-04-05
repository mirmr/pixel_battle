from contextlib import contextmanager
from typing import Iterator, Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, Connection, Transaction

from pixel_battle.config import app_config


class DatabaseManager:
    _active_connection: Optional[Connection] = None

    def __init__(self):
        self._engine: Engine = create_engine(app_config.db.url)
        self._active_sessions = 0

    @property
    def _connection(self) -> Connection:
        if self._active_connection is None:
            self._active_connection = self._engine.connect()
        assert self._active_connection is not None
        return self._active_connection

    @_connection.deleter
    def _connection(self) -> None:
        if self._active_connection is not None:
            self._active_connection.close()
            self._active_connection = None

    @contextmanager
    def session(self, nested: bool = False) -> Iterator[Connection]:

        transaction: Optional[Transaction]
        if nested:
            transaction = self._connection.begin_nested()
        elif self._connection.in_transaction():
            transaction = None
        else:
            transaction = self._connection.begin()

        if transaction is not None:
            self._active_sessions += 1

        try:
            yield self._connection
            if transaction:
                transaction.commit()
        except Exception as ex:
            if transaction:
                transaction.rollback()
            raise ex
        finally:
            if transaction:
                self._active_sessions -= 1
                if self._active_sessions == 0:
                    del self._connection
