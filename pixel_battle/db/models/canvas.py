from datetime import datetime

from pixel_battle.db.models import BaseRepository
from pixel_battle.db.tables import canvases
from pixel_battle.exceptions import CanvasNotFoundError


class Canvas:
    __slots__ = ("id", "account_id", "name", "width", "height", "active_from", "active_to", "updated_at", "created_at")

    def __init__(
        self,
        id_: str,
        account_id: int,
        name: str,
        width: int,
        height: int,
        active_from: datetime,
        active_to: datetime,
        updated_at: datetime,
        created_at: datetime,
    ) -> None:
        self.id = id_
        self.account_id = account_id
        self.name = name
        self.width = width
        self.height = height
        self.active_from = active_from
        self.active_to = active_to
        self.updated_at = updated_at
        self.created_at = created_at

    def __repr__(self) -> str:
        return f'<Token(id={self.id}, account_id={self.account_id}, created_at="{self.created_at}")>'


class CanvasRepository(BaseRepository[Canvas, int]):
    _row_not_found_error = CanvasNotFoundError
    table = canvases

    def _row_to_instance(self, row) -> Canvas:
        return Canvas(
            id_=row.id,
            account_id=row.account_id,
            name=row.name,
            width=row.width,
            height=row.height,
            active_from=row.active_from,
            active_to=row.active_to,
            updated_at=row.updated_at,
            created_at=row.created_at,
        )
