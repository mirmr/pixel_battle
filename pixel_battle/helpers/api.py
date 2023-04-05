import re
from datetime import datetime
from json import dumps, loads
from typing import Any, Callable, Dict, Optional

import fastjsonschema
from falcon import HTTPBadRequest, HTTPError, HTTPInvalidHeader, Request, Response

from pixel_battle.exceptions import (
    AccountNotFoundError,
    InternalServerError,
    ProjectError,
    RequestValidationError,
    ResponseValidationError,
)
from pixel_battle.logic.account_service import AccountService


class BaseResource:
    @classmethod
    def get_as_datetime(cls, req: Request, name: str, required: bool) -> Optional[datetime]:
        val = req.media.get(name)
        if not val:
            if required:
                raise HTTPBadRequest(description=f"{name} is required")
            return None

        try:
            return datetime.strptime(val, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError as ex:
            raise HTTPBadRequest(description=f"{name}: {ex}")


class http_request:
    _request_validator: Optional[Callable[[Dict], Dict]]
    _response_validator: Optional[Callable[[Dict], Dict]]

    def __init__(self, request_schema: str = None, response_schema: str = None) -> None:
        if request_schema is not None:
            with open("/".join(["pixel_battle/api/schemas", request_schema]), "rt", encoding="utf-8") as fin:
                self._request_validator = fastjsonschema.compile(loads(fin.read()))
        else:
            self._request_validator = None

        if response_schema is not None:
            with open("/".join(["pixel_battle/api/schemas", response_schema]), "rt", encoding="utf-8") as fin:
                self._response_validator = fastjsonschema.compile(loads(fin.read()))
        else:
            self._response_validator = None

    def __call__(self, func: Callable) -> Callable:
        def wrapper(*args, **kwargs: Any):
            try:
                req = args[1]
                resp = args[2]
                if self._request_validator:
                    try:
                        self._request_validator(req.media)
                    except Exception as ex:
                        raise RequestValidationError(str(ex))

                result = func(*args, **kwargs)

                if self._response_validator:
                    try:
                        self._response_validator(result)
                    except Exception as ex:
                        raise ResponseValidationError(str(ex))

                resp.text = dumps(result, ensure_ascii=False)
            except HTTPError as ex:
                raise ex
            except ProjectError as ex:
                raise InternalServerError(str(ex) or ex.__class__.__name__)

        return wrapper


def auth_required(req: Request, resp: Response, resource: BaseResource, params: Dict[str, Any]):
    auth_header = req.get_header("Authentication", required=True)
    pattern = r"Bearer ([a-f0-9]+)"
    matches = re.findall(pattern, auth_header)
    if len(matches) == 0 or len(matches) > 1:
        raise HTTPInvalidHeader(header_name="Authentication", msg=f'Header must match pattern "{pattern}"')
    token_id = matches[0]
    try:
        account = AccountService().get_account_by_token_id(token_id)
    except AccountNotFoundError as ex:
        raise HTTPInvalidHeader(header_name="Authentication", msg=f"Unknown token") from ex
    params["account"] = account
