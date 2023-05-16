from typing import Any, Dict, List

from falcon import App, Request, Response

from pixel_battle.api.routes import routes

app = App()


def get_routes(routes_dict: Dict) -> List:
    result = []
    for base_route, value in routes_dict.items():
        if isinstance(value, dict):
            for route_, resource_ in get_routes(value):
                result.append(("/".join([base_route, route_]), resource_))
        else:
            result.append((base_route, value))
    return result


class CorsMiddleware:
    def __init__(self, host: str):
        self.host = host

    def process_response(self, req: Request, resp: Response, resource: Any | None, req_succeeded: bool) -> None:
        resp.set_header('Access-Control-Allow-Origin', self.host)
        resp.set_header('Access-Control-Allow-Credentials', 'true')
        resp.set_header('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS')
        if header := req.get_header('Access-Control-Request-Headers'):
            resp.set_header('Access-Control-Allow-Headers', header)

for route, resource in get_routes(routes):
    app.add_route(route, resource)