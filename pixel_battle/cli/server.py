from typing import List, Tuple

from click import group, option


@group("server")
def server() -> None:
    """
    Group for managing web-server
    """
    pass


@server.command("run")
@option("--port", "-p", "port", type=int, default=8000, show_default=True)
def run(port: int) -> None:
    """
    Run server
    """
    from werkzeug import run_simple
    from pixel_battle.api import app
    from pixel_battle.api import CorsMiddleware

    host = "localhost"

    app.add_middleware(CorsMiddleware(host))

    run_simple(host, port, app, use_reloader=True)


@server.command("routes")
def routes() -> None:
    """
    List all routes
    """
    from pixel_battle.api import app
    from pixel_battle.helpers.api import BaseResource
    from falcon.routing.compiled import CompiledRouterNode

    routes_list: List[Tuple[str, BaseResource]] = []

    def get_children(node: CompiledRouterNode) -> None:
        if len(node.children):
            for child_node in node.children:
                get_children(child_node)
        if node.resource:
            routes_list.append((node.uri_template, node.resource))

    list(map(get_children, app._router._roots))

    def get_methods(resource: BaseResource) -> List[str]:
        res = []
        for method in ("get", "post", "patch", "delete"):
            if hasattr(resource, f"on_{method}"):
                res.append(method.upper())
        return res

    for route, resource in sorted(routes_list, key=lambda x: x[0]):
        print(f"{route}: {get_methods(resource)}")
