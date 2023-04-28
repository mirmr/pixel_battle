from falcon import Request, Response

from pixel_battle.helpers.api import BaseResource, http_request


class PingResource(BaseResource):
    @classmethod
    @http_request(response_schema="ping/get_response.json")
    def on_get(cls, req: Request, resp: Response):
        return "pong"
