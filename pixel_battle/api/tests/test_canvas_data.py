import pytest
from falcon import HTTP_200, HTTP_400, HTTP_429
from falcon.testing import TestClient

from pixel_battle.api.tests.conftest import CANVAS_SIZE
from pixel_battle.db.models.canvas import Canvas


def test_fill_pixel_no_authentication(canvas: Canvas, client: TestClient) -> None:
    json = {
        "x": 1,
        "y": 1,
        "color": "black",
    }

    response = client.simulate_post(
        f"/canvas/{canvas.id}/data",
        json=json,
    )

    assert response.status == HTTP_400


def test_fill_pixel_invalid_token(canvas: Canvas, client: TestClient) -> None:
    json = {
        "x": 1,
        "y": 1,
        "color": "black",
    }

    headers = {
        "Authentication": f"Bearer asdfasdfwf",
    }

    response = client.simulate_post(
        f"/canvas/{canvas.id}/data",
        json=json,
        headers=headers,
    )

    assert response.status == HTTP_400


def test_fill_pixel_invalid_header(canvas: Canvas, client: TestClient) -> None:
    json = {
        "x": 1,
        "y": 1,
        "color": "black",
    }

    headers = {
        "Authentication": f"Bearerasdfasdfwf",
    }

    response = client.simulate_post(
        f"/canvas/{canvas.id}/data",
        json=json,
        headers=headers,
    )

    assert response.status == HTTP_400


@pytest.mark.parametrize("has_x", (True, False))
@pytest.mark.parametrize("has_y", (True, False))
@pytest.mark.parametrize("has_color", (True, False))
def test_fill_pixel_missing_properties(
    canvas: Canvas, token: str, client: TestClient, has_x: bool, has_y: bool, has_color: bool
) -> None:
    json = {}
    if has_x:
        json["x"] = 1
    if has_y:
        json["y"] = 1
    if has_color:
        json["color"] = "black"

    headers = {
        "Authentication": f"Bearer {token}",
    }

    response = client.simulate_post(
        f"/canvas/{canvas.id}/data",
        json=json,
        headers=headers,
    )

    expected_status = HTTP_200 if (has_x and has_y and has_color) else HTTP_400
    assert response.status == expected_status


@pytest.mark.parametrize("x", (-10, -1, CANVAS_SIZE, 9999999))
def test_fill_pixel_x_out_of_bounds(canvas: Canvas, token: str, client: TestClient, x: int) -> None:
    json = {
        "y": 1,
        "x": x,
        "color": "black",
    }

    headers = {
        "Authentication": f"Bearer {token}",
    }

    response = client.simulate_post(
        f"/canvas/{canvas.id}/data",
        json=json,
        headers=headers,
    )

    assert response.status == HTTP_400


@pytest.mark.parametrize("y", (-10, -1, CANVAS_SIZE, 9999999))
def test_fill_pixel_y_out_of_bounds(canvas: Canvas, token: str, client: TestClient, y: int) -> None:
    json = {
        "y": y,
        "x": 1,
        "color": "black",
    }

    headers = {
        "Authentication": f"Bearer {token}",
    }

    response = client.simulate_post(
        f"/canvas/{canvas.id}/data",
        json=json,
        headers=headers,
    )

    assert response.status == HTTP_400


def test_fill_pixel_time_limit(canvas: Canvas, token: str, client: TestClient, new_canvas_log: None) -> None:
    json = {
        "y": 1,
        "x": 1,
        "color": "black",
    }

    headers = {
        "Authentication": f"Bearer {token}",
    }

    response = client.simulate_post(
        f"/canvas/{canvas.id}/data",
        json=json,
        headers=headers,
    )

    assert response.status == HTTP_429
