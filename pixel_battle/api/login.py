from falcon import Request, Response

from pixel_battle.helpers.api import BaseResource, http_request
from pixel_battle.logic.account_service import AccountService


class LoginResource(BaseResource):
    @classmethod
    @http_request(request_schema="login/request.json", response_schema="login/response.json")
    def on_post(cls, req: Request, resp: Response):
        name = req.media["name"]
        password = req.media["password"]

        account_service = AccountService()
        account = account_service.login(name, password)
        token = account_service.generate_token(account)

        return {
            "account_id": account.id,
            "account_name": account.name,
            "token": token.id,
            "created_at": token.created_at.isoformat(),
        }
