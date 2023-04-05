import falcon
from falcon import HTTPBadRequest, HTTPForbidden, HTTPNotFound, Request, Response

from pixel_battle.db.models.account import Account
from pixel_battle.exceptions import CanvasNotFoundError
from pixel_battle.helpers import db_manager
from pixel_battle.helpers.api import auth_required, BaseResource, http_request
from pixel_battle.logic.canvas_service import CanvasService


class CanvasResource(BaseResource):
    @classmethod
    @falcon.before(auth_required)
    @http_request(request_schema="canvas/request.json", response_schema="canvas/response.json")
    def on_post(cls, req: Request, resp: Response, account: Account):
        name = req.media["name"]
        width = req.media["width"]
        height = req.media["height"]
        active_from = cls.get_as_datetime(req, "active_from", required=True)
        active_to = cls.get_as_datetime(req, "active_to", required=True)
        if active_from >= active_to:
            raise HTTPBadRequest(description="active_to must be later than active_from")

        canvas_service = CanvasService()
        canvas = canvas_service.create_canvas(
            account_id=account.id,
            name=name,
            width=width,
            height=height,
            active_from=active_from,
            active_to=active_to,
        )

        return {
            "id": canvas.id,
            "account_id": canvas.account_id,
            "name": canvas.name,
            "width": canvas.width,
            "height": canvas.height,
            "active_from": canvas.active_from.isoformat(),
            "active_to": canvas.active_to.isoformat(),
            "updated_at": canvas.updated_at.isoformat(),
            "created_at": canvas.created_at.isoformat(),
        }


class CanvasManagementResource(BaseResource):
    @classmethod
    @falcon.before(auth_required)
    @http_request(
        request_schema="canvas_management/patch_request.json", response_schema="canvas_management/patch_response.json"
    )
    def on_patch(cls, req: Request, resp: Response, canvas_id: int, account: Account):
        name = req.media.get("name")
        width = req.media.get("width")
        height = req.media.get("height")
        active_from = cls.get_as_datetime(req, "active_from", required=False)
        active_to = cls.get_as_datetime(req, "active_to", required=False)
        canvas_service = CanvasService()
        with db_manager.session():
            try:
                canvas = canvas_service.get_by_id(canvas_id)
            except CanvasNotFoundError as ex:
                raise HTTPNotFound(description=f"Canvas {canvas_id} not found") from ex

            if canvas.account_id != account.id:
                raise HTTPForbidden(description=f"Only creator can edit canvas")

            canvas = canvas_service.update(
                canvas,
                name,
                width,
                height,
                active_from,
                active_to,
            )

            return {
                "id": canvas.id,
                "account_id": canvas.account_id,
                "name": canvas.name,
                "width": canvas.width,
                "height": canvas.height,
                "active_from": canvas.active_from.isoformat(),
                "active_to": canvas.active_to.isoformat(),
                "updated_at": canvas.updated_at.isoformat(),
                "created_at": canvas.created_at.isoformat(),
            }

    @classmethod
    @http_request(response_schema="canvas_management/get_response.json")
    def on_get(cls, req: Request, resp: Response, canvas_id: int):
        canvas_service = CanvasService()
        with db_manager.session():
            try:
                canvas = canvas_service.get_by_id(canvas_id)
            except CanvasNotFoundError as ex:
                raise HTTPNotFound(description=f"Canvas {canvas_id} not found") from ex

            return {
                "id": canvas.id,
                "account_id": canvas.account_id,
                "name": canvas.name,
                "width": canvas.width,
                "height": canvas.height,
                "active_from": canvas.active_from.isoformat(),
                "active_to": canvas.active_to.isoformat(),
                "updated_at": canvas.updated_at.isoformat(),
                "created_at": canvas.created_at.isoformat(),
            }