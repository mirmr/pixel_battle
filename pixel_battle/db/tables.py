from sqlalchemy import Table, MetaData, Column, BigInteger, DateTime, Boolean, ForeignKey, Text, Integer
from sqlalchemy.sql.functions import now


meta = MetaData()

accounts = Table(
    "accounts",
    meta,
    Column("id", BigInteger, nullable=False, autoincrement=True, primary_key=True),
    Column("name", Text, nullable=False, unique=True),
    Column("password_hash", Text, nullable=False),
    Column("created_at", DateTime, nullable=False, default=now(), server_default=now()),
    Column("updated_at", DateTime, nullable=False, default=now(), server_default=now()),
)

tokens = Table(
    "tokens",
    meta,
    Column("id", Text, nullable=False, primary_key=True),
    Column("account_id", BigInteger, ForeignKey(accounts.c.id, ondelete="CASCADE"), nullable=False),
    Column("created_at", DateTime, nullable=False, default=now(), server_default=now()),
)

canvases = Table(
    "canvases",
    meta,
    Column("id", BigInteger, nullable=False, autoincrement=True, primary_key=True),
    Column("account_id", BigInteger, ForeignKey(accounts.c.id, ondelete="SET NULL"), nullable=True),
    Column("name", Text, nullable=False),
    Column("width", Integer, nullable=False),
    Column("height", Integer, nullable=False),
    Column("active_from", DateTime, nullable=False),
    Column("active_to", DateTime, nullable=False),
    Column("created_at", DateTime, nullable=False, default=now(), server_default=now()),
    Column("updated_at", DateTime, nullable=False, default=now(), server_default=now()),
)

canvas_log = Table(
    "canvas_log",
    meta,
    Column("id", BigInteger, nullable=False, autoincrement=True, primary_key=True),
    Column("account_id", BigInteger, ForeignKey(accounts.c.id, ondelete="SET NULL"), nullable=True),
    Column("canvas_id", BigInteger, ForeignKey(canvases.c.id, ondelete="CASCADE"), nullable=False),
    Column("x", Integer, nullable=False),
    Column("y", Integer, nullable=False),
    Column("color", Text, nullable=False),
    Column("created_at", DateTime, nullable=False, default=now(), server_default=now()),
)
