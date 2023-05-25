from datetime import datetime, timedelta
from typing import Generator
from unittest.mock import MagicMock

import pytest
from _pytest.monkeypatch import MonkeyPatch
from alembic import command
from falcon import testing
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy_utils import create_database, database_exists, drop_database

from pixel_battle.api import app
from pixel_battle.config import app_config
from pixel_battle.db import account_repo, canvas_repo
from pixel_battle.db.alembic.utils import get_alembic_config
from pixel_battle.db.models.account import Account
from pixel_battle.db.models.canvas import Canvas
from pixel_battle.logic.account_service import AccountService
from pixel_battle.logic.canvas_service import CanvasService


CANVAS_SIZE = 50


@pytest.fixture(scope="session")
def monkeysession() -> Generator[MonkeyPatch, None, None]:
    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture(autouse=True, scope="session")
def db(monkeysession: MonkeyPatch) -> None:
    db_test_url_str = app_config.db.url
    db_url = make_url(db_test_url_str)

    db_url = db_url.set(database=f"{db_url.database}_test")
    db_test_url_str = str(db_url)

    if database_exists(db_test_url_str):
        drop_database(db_test_url_str)
    create_database(db_test_url_str)

    alembic_config = get_alembic_config()
    monkeysession.setattr("pixel_battle.config.app_config.db", MagicMock(url=db_test_url_str))
    command.upgrade(alembic_config, "head")

    test_engine = create_engine(
        db_test_url_str,
    )

    monkeysession.setattr("pixel_battle.helpers.db_manager._engine", test_engine)

    yield None
    command.downgrade(alembic_config, "base")


@pytest.fixture()
def client() -> testing.TestClient:
    app.req_options.strip_url_path_trailing_slash = True
    return testing.TestClient(app)


@pytest.fixture()
def account_password() -> str:
    return "password123"


@pytest.fixture()
def account_name() -> str:
    return "test_user"


@pytest.fixture()
def account(account_password: str, account_name: str) -> Account:
    account_service = AccountService()
    account = account_service.create(account_name, account_password)
    yield account
    account_repo.delete_all()


@pytest.fixture()
def token(account: Account) -> str:
    yield AccountService().generate_token(account).id


@pytest.fixture()
def canvas(account: Account) -> Canvas:
    canvas_service = CanvasService()
    now = datetime.utcnow()
    canvas = canvas_service.create_canvas(
        account_id=account.id,
        name="test_canvas",
        width=CANVAS_SIZE,
        height=CANVAS_SIZE,
        active_from=now - timedelta(days=1),
        active_to=now + timedelta(days=1),
    )
    yield canvas
    canvas_repo.delete_all()


@pytest.fixture()
def new_canvas_log(account: Account, canvas: Canvas) -> None:
    canvas_service = CanvasService()
    canvas_service.fill_pixel(0, 0, "black", canvas, account)
