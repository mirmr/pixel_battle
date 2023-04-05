from datetime import datetime

from falcon import HTTPBadRequest

from pixel_battle.db import canvas_repo
from pixel_battle.db.models.canvas import Canvas
from pixel_battle.helpers import db_manager


class CanvasService:
    def create_canvas(
        self,
        account_id: int,
        name: str,
        width: int,
        height: int,
        active_from: datetime,
        active_to: datetime,
    ) -> Canvas:
        with db_manager.session():
            return canvas_repo.create(
                account_id=account_id,
                name=name,
                width=width,
                height=height,
                active_from=active_from,
                active_to=active_to,
            )

    def get_by_id(self, canvas_id: int) -> Canvas:
        return canvas_repo.get_by_id(canvas_id)

    def update(
        self,
        canvas: Canvas,
        name: str,
        width: int,
        height: int,
        active_from: datetime,
        active_to: datetime,
    ) -> Canvas:
        canvas.name = name or canvas.name
        canvas.width = width or canvas.width
        canvas.height = height or canvas.height
        canvas.active_from = active_from or canvas.active_from
        canvas.active_to = active_to or canvas.active_to

        if canvas.active_from >= canvas.active_to:
            raise HTTPBadRequest(description="active_to must be later than active_from")

        canvas_repo.update(canvas)
        return canvas
