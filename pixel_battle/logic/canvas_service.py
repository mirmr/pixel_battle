from datetime import datetime, timedelta
from math import ceil
from typing import Tuple

from falcon import HTTPBadRequest

from pixel_battle.config import app_config
from pixel_battle.db import canvas_log_repo, canvas_repo
from pixel_battle.db.models.account import Account
from pixel_battle.db.models.canvas import Canvas
from pixel_battle.db.models.canvas_log import CanvasLog
from pixel_battle.exceptions import RateLimitExceeded
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

    def get_next_xy(self, canvas: Canvas, x: int, y: int) -> Tuple[int, int] | None:
        x += 1
        if x >= canvas.width:
            x = 0
            y += 1
            if y >= canvas.height:
                return None
        return x, y

    def get_canvas_state(self, canvas: Canvas, time: datetime) -> list[list[str]]:
        with db_manager.session():
            color_data = canvas_log_repo.get_latest_log(canvas.width - 1, canvas.height - 1, canvas.id, time)
        color_data.append((None, None, None))
        result: list[list[str]] = []
        default_color = "white"
        current_x = 0
        current_y = 0
        done = False
        for x, y, color in color_data:
            while (current_x, current_y) != (x, y) and not done:
                if len(result) == current_y:
                    result.append([])
                result[current_y].append(default_color)
                if (next_coords := self.get_next_xy(canvas, current_x, current_y)) is None:
                    done = True
                    break
                else:
                    current_x, current_y = next_coords

            if done:
                break

            if len(result) == current_y:
                result.append([])
            result[current_y].append(color)
            if (next_coords := self.get_next_xy(canvas, x, y)) is None:
                done = True
                break
            else:
                current_x, current_y = next_coords
        return result

    def fill_pixel(self, x: int, y: int, color: str, canvas: Canvas, account: Account) -> None:
        if x >= canvas.width:
            raise RuntimeError()
        if y >= canvas.height:
            raise RuntimeError()

        current_time = datetime.utcnow()
        if (
            last_update_time := canvas_log_repo.has_update(
                canvas.id, account.id, current_time - timedelta(seconds=app_config.app.cooldown)
            )
        ) is not None:
            allowed_time = last_update_time + timedelta(seconds=app_config.app.cooldown)
            time_to_wait = ceil((allowed_time - current_time).total_seconds())
            raise RateLimitExceeded(retry_after=time_to_wait)

        canvas_log_repo.create(
            account_id=account.id,
            canvas_id=canvas.id,
            x=x,
            y=y,
            color=color,
            created_at=current_time,
        )
