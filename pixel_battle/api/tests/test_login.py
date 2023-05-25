from falcon import HTTP_200, HTTP_400
from falcon.testing import TestClient

from pixel_battle.db.models.account import Account
from pixel_battle.logic.account_service import AccountService


def test_login_ok(account: Account, account_password: str, client: TestClient) -> None:
    json = {
        "name": account.name,
        "password": account_password,
    }
    response = client.simulate_post("/login", json=json)

    assert response.status == HTTP_200
    assert response.json["account_id"] == account.id
    assert response.json["account_name"] == account.name

    assert account == AccountService().get_account_by_token_id(response.json["token"])


def test_login_invalid_password(account: Account, account_password: str, client: TestClient) -> None:
    json = {
        "name": account.name,
        "password": account_password + "invalid",
    }
    response = client.simulate_post("/login", json=json)

    assert response.status == HTTP_400


def test_invalid_name_and_password_have_same_response(account: Account, account_password, client: TestClient) -> None:
    json = {
        "name": account.name,
        "password": account_password + "invalid",
    }
    response_password = client.simulate_post("/login", json=json)

    json = {
        "name": account.name + "invalid",
        "password": account_password,
    }
    response_name = client.simulate_post("/login", json=json)

    assert response_name.status_code == response_password.status_code
    assert response_name.json == response_password.json


def test_login_invalid_name(account: Account, account_password: str, client: TestClient) -> None:
    json = {
        "name": account.name + "invalid",
        "password": account_password,
    }
    response = client.simulate_post("/login", json=json)

    assert response.status == HTTP_400


def test_login_no_name(account: Account, account_password: str, client: TestClient) -> None:
    json = {
        "password": account_password,
    }
    response = client.simulate_post("/login", json=json)

    assert response.status == HTTP_400


def test_login_no_password(account: Account, account_password: str, client: TestClient) -> None:
    json = {
        "name": account.name,
    }
    response = client.simulate_post("/login", json=json)

    assert response.status == HTTP_400
