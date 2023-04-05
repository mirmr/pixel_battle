from falcon import HTTPBadRequest, HTTPInternalServerError, HTTPNotFound, HTTPConflict


class ProjectError(Exception):
    pass


class BaseHTTPError(ProjectError):
    def __init__(self, description: str):
        # Error is used with HTTPError so call to super init is valid
        super(BaseHTTPError, self).__init__(title=self.__class__.__name__, description=description)  # type: ignore


class RequestValidationError(BaseHTTPError, HTTPBadRequest):
    pass


class ResponseValidationError(BaseHTTPError, HTTPBadRequest):
    pass


class BadParameterError(BaseHTTPError, HTTPBadRequest):
    pass


class NotFoundError(BaseHTTPError, HTTPNotFound):
    pass


class InternalServerError(BaseHTTPError, HTTPInternalServerError):
    pass


class ConflictError(BaseHTTPError, HTTPConflict):
    pass


class LoginError(BaseHTTPError, HTTPBadRequest):
    pass


class IntegrityError(ProjectError):
    pass


class RowNotFoundError(IntegrityError):
    pass


class AccountNotFoundError(RowNotFoundError):
    pass


class TokenNotFoundError(RowNotFoundError):
    pass


class CanvasNotFoundError(RowNotFoundError):
    pass
