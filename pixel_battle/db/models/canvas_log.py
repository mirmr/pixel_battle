from datetime import datetime
from typing import List, Tuple

from sqlalchemy import and_, bindparam, func, select
from sqlalchemy.engine import Connection, Result, Row

from pixel_battle.db.models import BaseRepository
from pixel_battle.db.tables import canvas_log
from pixel_battle.exceptions import CanvasLogNotFoundError
from pixel_battle.helpers import db_manager


class CanvasLog:
    __slots__ = ("id", "account_id", "canvas_id", "x", "y", "color", "created_at")

    def __init__(
        self,
        id_: str,
        account_id: int,
        canvas_id: int,
        x: int,
        y: int,
        color: str,
        created_at: datetime,
    ) -> None:
        self.id = id_
        self.account_id = account_id
        self.canvas_id = canvas_id
        self.x = x
        self.y = y
        self.color = color
        self.created_at = created_at

    def __repr__(self) -> str:
        return f'<CanvasLog(id={self.id}, canvas_id={self.canvas_id}, created_at="{self.created_at}")>'


class CanvasLogRepository(BaseRepository[CanvasLog, int]):
    _row_not_found_error = CanvasLogNotFoundError
    table = canvas_log

    def _row_to_instance(self, row: Row) -> CanvasLog:
        return CanvasLog(
            id_=row.id,
            account_id=row.account_id,
            canvas_id=row.canvas_id,
            x=row.x,
            y=row.y,
            color=row.color,
            created_at=row.created_at,
        )

    def get_latest_log(self, max_x: int, max_y: int, canvas_id: int, time: datetime) -> List[Tuple[int, int, str]]:
        latest_log_subq = (
            select(
                self.table.c.canvas_id,
                self.table.c.x,
                self.table.c.y,
                func.max(self.table.c.created_at).label("max_created_at"),
            )
            .where(
                self.table.c.canvas_id == bindparam("b_canvas_id"),
                self.table.c.created_at <= bindparam("b_datetime"),
                self.table.c.x <= bindparam("b_max_x"),
                self.table.c.y <= bindparam("b_max_y"),
            )
            .group_by(
                self.table.c.canvas_id,
                self.table.c.x,
                self.table.c.y,
            )
            .subquery()
        )

        query = (
            select(
                self.table.c.x,
                self.table.c.y,
                self.table.c.color,
            )
            .join(
                latest_log_subq,
                and_(
                    self.table.c.canvas_id == latest_log_subq.c.canvas_id,
                    self.table.c.x == latest_log_subq.c.x,
                    self.table.c.y == latest_log_subq.c.y,
                    self.table.c.created_at == latest_log_subq.c.max_created_at,
                ),
            )
            .order_by(
                self.table.c.y,
                self.table.c.x,
            )
        )

        params = {
            "b_canvas_id": canvas_id,
            "b_datetime": time,
            "b_max_x": max_x,
            "b_max_y": max_y,
        }

        with db_manager.session() as db:
            res: Result = db.execute(query, **params)

        return [(row.x, row.y, row.color) for row in res]

    def has_update(self, canvas_id: int, account_id: int, min_created_at: datetime) -> datetime | None:
        query = (
            select(
                self.table.c.created_at,
            )
            .select_from(
                self.table,
            )
            .where(
                self.table.c.canvas_id == bindparam("b_canvas_id"),
                self.table.c.account_id == bindparam("b_account_id"),
                self.table.c.created_at >= bindparam("b_min_created_at"),
            )
            .order_by(
                self.table.c.created_at.desc(),
            )
            .limit(1)
        )

        params = {
            "b_canvas_id": canvas_id,
            "b_account_id": account_id,
            "b_min_created_at": min_created_at,
        }

        with db_manager.session() as db:
            res: Result = db.execute(query, **params)

        return res.scalar_one_or_none()
