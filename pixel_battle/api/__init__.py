from typing import Dict, List

from falcon import App

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


for route, resource in get_routes(routes):
    app.add_route(route, resource)
