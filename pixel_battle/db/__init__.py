from pixel_battle.db.models.account import AccountRepository
from pixel_battle.db.models.canvas import CanvasRepository
from pixel_battle.db.models.canvas_log import CanvasLogRepository
from pixel_battle.db.models.token import TokenRepository

account_repo = AccountRepository()
token_repo = TokenRepository()
canvas_repo = CanvasRepository()
canvas_log_repo = CanvasLogRepository()
