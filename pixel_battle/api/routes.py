from pixel_battle.api.account import AccountResource
from pixel_battle.api.canvas import CanvasManagementResource, CanvasResource, UserCanvasesResource
from pixel_battle.api.canvas_data import CanvasDataResource
from pixel_battle.api.login import LoginResource
from pixel_battle.api.ping import PingResource

routes = {
    "/account": AccountResource(),
    "/login": LoginResource(),
    "/canvas": CanvasResource(),
    "/canvas/my": UserCanvasesResource(),
    "/canvas/{canvas_id:int}": CanvasManagementResource(),
    "/canvas/{canvas_id:int}/data": CanvasDataResource(),
    "/ping": PingResource(),
}
