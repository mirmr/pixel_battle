from datetime import datetime
from functools import cached_property
from typing import Tuple, TypeVar, Generic, List

from sqlalchemy import Table, Column, bindparam
from sqlalchemy.engine import Row, CursorResult, Result
from sqlalchemy.exc import IntegrityError as SqlIntegrityError
from sqlalchemy.sql import Insert, Select, Delete, Update

from pixel_battle.exceptions import IntegrityError, RowNotFoundError
from pixel_battle.helpers import db_manager

T = TypeVar("T")
T_ID = TypeVar("T_ID")


class BaseRepository(Generic[T, T_ID]):
    _row_not_found_error = RowNotFoundError
    table: Table

    def _row_to_instance(self, row) -> T:
        raise NotImplementedError()

    @cached_property
    def updatable_columns(self) -> Tuple[Column, ...]:
        return tuple(c for c in self.table.c if (c != self.id_column and c.key != "created_at"))

    @cached_property
    def id_column(self) -> Column:
        for c in self.table.primary_key:
            return c

    def _insert_q(self) -> Insert:
        return (
            self.table.insert()
            .returning(
                self.table,
            )
            .values()
        )

    def _get_q(self) -> Select:
        return self.table.select()

    def _delete_q(self) -> Delete:
        return self.table.delete()

    def _get_by_id_q(self) -> Select:
        return self._get_q().where(
            self.id_column == bindparam(f"b_{self.id_column.key}"),
        )

    def _update_by_id_q(self) -> Update:
        return (
            self.table.update()
            .where(
                self.id_column == bindparam(f"b_{self.id_column.key}"),
            )
            .values({c: bindparam(f"b_{c.key}") for c in self.updatable_columns})
        )

    def _one(self, result: CursorResult) -> Row:
        rows = result.fetchall()
        if len(rows) == 0:
            raise self._row_not_found_error()
        if len(rows) > 1:
            raise IntegrityError()
        return rows[0]

    def get_all(self) -> List[T]:
        with db_manager.session() as db:
            return list(map(self._row_to_instance, db.execute(self._get_q()).fetchall()))

    def delete_all(self) -> None:
        with db_manager.session() as db:
            db.execute(self._delete_q())

    def update(self, instance: T) -> None:
        with db_manager.session() as db:
            instance.updated_at = datetime.utcnow()
            params = {f"b_{c.key}": getattr(instance, c.key) for c in self.updatable_columns}
            params[f"b_{self.id_column.key}"] = getattr(instance, self.id_column.key)
            db.execute(self._update_by_id_q(), **params)

    def create(self, **kwargs) -> T:
        with db_manager.session() as db:
            try:
                res: Result = db.execute(self._insert_q(), **kwargs)
            except SqlIntegrityError as ex:
                raise IntegrityError(str(ex))
            return self._row_to_instance(self._one(res))

    def get_by_id(self, id: T_ID) -> T:
        with db_manager.session() as db:
            params = {
                f"b_{self.id_column.key}": id,
            }
            res: Result = db.execute(self._get_by_id_q(), **params)
            return self._row_to_instance(self._one(res))
