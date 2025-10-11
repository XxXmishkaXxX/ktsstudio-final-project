from app.services.game import GameService
from app.services.renderer import GameRenderer
from app.services.round.round_service import RoundService
from app.services.timer import TimerService


def setup_services(app):
    app.timer_service = TimerService(app)
    app.renderer = GameRenderer(app)
    app.round_service = RoundService(app)
    app.game_service = GameService(app)
