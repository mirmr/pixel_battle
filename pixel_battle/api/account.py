import falcon
from falcon import Request, Response

from pixel_battle.db import account_repo
from pixel_battle.db.models.account import Account
from pixel_battle.exceptions import AccountNotFoundError, NotFoundError
from pixel_battle.helpers import db_manager
from pixel_battle.helpers.api import http_request, BaseResource, auth_required
from pixel_battle.logic.account_service import AccountService


class AccountResource(BaseResource):
    @classmethod
    @http_request(response_schema="account/get_response.json")
    def on_get(cls, req: Request, resp: Response):
        g_id = req.get_param_as_int("g_id", required=True)
        assert g_id is not None

        with db_manager.session():
            try:
                account = account_repo.get_by_g_id(g_id=g_id)
            except AccountNotFoundError:
                raise NotFoundError("Account not found")
            return {
                "account_id": account.id,
                "g_id": account.g_id,
                "created_at": str(account.created_at),
                "updated_at": str(account.updated_at),
            }

    @classmethod
    @falcon.before(auth_required)
    @http_request(request_schema="account/patch_request.json", response_schema="account/get_response.json")
    def on_patch(cls, req: Request, resp: Response, account: Account):
        name = req.media.get("name")
        password = req.media.get("password")
        account = AccountService().update(account, name, password)

        return {
            "id": account.id,
            "name": account.name,
            "created_at": str(account.created_at),
            "updated_at": str(account.updated_at),
        }

    @classmethod
    @http_request(request_schema="account/post_request.json", response_schema="account/get_response.json")
    def on_post(cls, req: Request, resp: Response):
        name: str = req.media["name"]
        password: str = req.media["password"]

        account = AccountService().create(name, password)

        return {
            "id": account.id,
            "name": account.name,
            "created_at": str(account.created_at),
            "updated_at": str(account.updated_at),
        }
