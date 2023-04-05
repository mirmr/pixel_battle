from datetime import datetime

from pixel_battle.db.models import BaseRepository
from pixel_battle.db.tables import tokens
from pixel_battle.exceptions import TokenNotFoundError


class Token:
    __slots__ = ("id", "account_id", "created_at")

    def __init__(self, id_: str, account_id: int, created_at: datetime) -> None:
        self.id = id_
        self.account_id = account_id
        self.created_at = created_at

    def __repr__(self) -> str:
        return f'<Token(id={self.id}, account_id={self.account_id}, created_at="{self.created_at}")>'


class TokenRepository(BaseRepository[Token, int]):
    _row_not_found_error = TokenNotFoundError
    table = tokens

    def _row_to_instance(self, row) -> Token:
        return Token(
            id_=row.id,
            account_id=row.account_id,
            created_at=row.created_at,
        )
