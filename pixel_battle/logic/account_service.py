import secrets
from typing import Optional

from argon2 import PasswordHasher
from argon2.exceptions import Argon2Error

from pixel_battle.db import account_repo, token_repo
from pixel_battle.db.models.account import Account
from pixel_battle.db.models.token import Token
from pixel_battle.exceptions import IntegrityError, ConflictError, AccountNotFoundError, LoginError
from pixel_battle.helpers import db_manager


class AccountService:
    def create(self, name: str, password: str) -> Account:
        hasher = PasswordHasher()
        password_hash = hasher.hash(password)

        try:
            with db_manager.session():
                return account_repo.create(name=name, password_hash=password_hash)
        except IntegrityError as ex:
            raise ConflictError("AccountAlreadyExists")

    def update(self, account: Account, new_name: Optional[str], new_password: Optional[str]) -> Account:
        if new_name:
            account.name = new_name
        if new_password:
            hasher = PasswordHasher()
            account.password_hash = hasher.hash(new_password)

        try:
            with db_manager.session():
                account_repo.update(account)
        except IntegrityError as ex:
            raise ConflictError("AccountNameAlreadyTaken") from ex

        return account

    def login(self, name: str, password: str) -> Account:
        with db_manager.session():
            try:
                account = account_repo.get_by_name(name)
            except AccountNotFoundError as ex:
                raise LoginError("Login failed") from ex
            hasher = PasswordHasher()
            try:
                hasher.verify(account.password_hash, password)
            except Argon2Error as ex:
                print("PasswordMismatch")
                raise LoginError("Login failed")

            if hasher.check_needs_rehash(account.password_hash):
                account.password_hash = hasher.hash(password)
                account_repo.update(account)
        return account

    def generate_token(self, account: Account) -> Token:
        with db_manager.session():
            return token_repo.create(id=secrets.token_hex(), account_id=account.id)

    def get_account_by_token_id(self, token_id: str) -> Account:
        return account_repo.get_by_token_id(token_id)
