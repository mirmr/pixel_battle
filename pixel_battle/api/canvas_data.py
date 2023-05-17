from datetime import datetime

import falcon
from falcon import HTTPNotFound, Request, Response

from pixel_battle.db.models.account import Account
from pixel_battle.exceptions import CanvasNotFoundError
from pixel_battle.helpers import db_manager
from pixel_battle.helpers.api import auth_required, BaseResource, http_request
from pixel_battle.logic.canvas_service import CanvasService


class CanvasDataResource(BaseResource):
    @classmethod
    @http_request(response_schema="canvas_data/get_response.json")
    def on_get(cls, req: Request, resp: Response, canvas_id: int):
        canvas_service = CanvasService()
        with db_manager.session():
            try:
                canvas = canvas_service.get_by_id(canvas_id)
            except CanvasNotFoundError as ex:
                raise HTTPNotFound(description=f"Canvas {canvas_id} not found") from ex

            at = req.get_param_as_datetime("at", default=datetime.utcnow())

            return canvas_service.get_canvas_state(canvas, at)

    @classmethod
    @falcon.before(auth_required)
    @http_request(request_schema="canvas_data/post_request.json")
    def on_post(cls, req: Request, resp: Response, canvas_id: int, account: Account):
        canvas_service = CanvasService()
        with db_manager.session():
            try:
                canvas = canvas_service.get_by_id(canvas_id)
            except CanvasNotFoundError as ex:
                raise HTTPNotFound(description=f"Canvas {canvas_id} not found") from ex

            canvas_service.fill_pixel(
                x=req.media["x"],
                y=req.media["y"],
                color=req.media["color"],
                canvas=canvas,
                account=account,
            )
