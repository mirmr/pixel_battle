from datetime import datetime
from typing import Optional

from sqlalchemy import bindparam
from sqlalchemy.engine import Result
from sqlalchemy.sql import Select

from pixel_battle.db.models import BaseRepository
from pixel_battle.db.tables import accounts, tokens
from pixel_battle.exceptions import AccountNotFoundError
from pixel_battle.helpers import db_manager


class Account:
    __slots__ = ("id", "name", "password_hash", "created_at", "updated_at")

    def __init__(self, id_: int, name: str, password_hash: str, created_at: datetime, updated_at: datetime) -> None:
        self.id = id_
        self.name = name
        self.password_hash = password_hash
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self) -> str:
        return f'<Account(id={self.id}, name={self.name}, updated_at="{self.updated_at}")>'


class AccountRepository(BaseRepository[Account, int]):
    _row_not_found_error = AccountNotFoundError
    table = accounts
    tokens_table = tokens

    def _row_to_instance(self, row) -> Account:
        return Account(
            id_=row.id,
            name=row.name,
            password_hash=row.password_hash,
            updated_at=row.updated_at,
            created_at=row.created_at,
        )

    def _get_by_name_q(self) -> Select:
        return self._get_q().where(self.table.c.name == bindparam("b_name"))

    def _get_by_token_id_q(self) -> Select:
        return (
            self._get_q()
            .join(
                self.tokens_table,
                self.table.c.id == self.tokens_table.c.account_id,
            )
            .where(
                self.tokens_table.c.id == bindparam("b_token_id"),
            )
        )

    def get_by_name(self, name: str) -> Optional[Account]:
        with db_manager.session() as db:
            params = {
                "b_name": name,
            }
            res: Result = db.execute(self._get_by_name_q(), **params)
            return self._row_to_instance(self._one(res))

    def get_by_token_id(self, token_id: str) -> Account:
        with db_manager.session() as db:
            params = {
                "b_token_id": token_id,
            }
            res: Result = db.execute(self._get_by_token_id_q(), **params)
            return self._row_to_instance(self._one(res))
