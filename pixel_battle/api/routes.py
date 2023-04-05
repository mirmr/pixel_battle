from pixel_battle.api.account import AccountResource
from pixel_battle.api.canvas import CanvasManagementResource, CanvasResource
from pixel_battle.api.login import LoginResource
from pixel_battle.api.ping import PingResource

routes = {
    "/account": AccountResource(),
    "/login": LoginResource(),
    "/canvas": CanvasResource(),
    "/canvas/{canvas_id:int}": CanvasManagementResource(),
    "/ping": PingResource(),
}
