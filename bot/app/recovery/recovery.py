import asyncio
import typing

if typing.TYPE_CHECKING:
    from app.web.app import Application

from app.games.models.games import GameState


class RecoveryService:
    BATCH_SIZE = 100

    def __init__(self, app: "Application"):
        self.app = app

    async def recover_all_games(self):
        active_states = [GameState.starting, GameState.in_progress]
        offset = 0

        while True:
            games_batch = await self.app.store.games.get_games_by_states(
                active_states, limit=self.BATCH_SIZE, offset=offset
            )
            self.app.logger.info(games_batch)
            if not games_batch:
                break

            for game in games_batch:
                game_id = game.id
                chat_id = game.chat_id
                message_id = await self.app.cache.pool.get(
                    f"game:{game_id}:message_id"
                )
                message_id = int(message_id) if message_id else None

                lock_key = f"game:{game_id}:lock"

                acquired = await self.app.cache.pool.set(
                    lock_key, "1", nx=True, ex=5
                )
                if not acquired:
                    continue

                current_round_id = (
                    await self.app.store.games.get_current_round_id(game_id)
                )
                if current_round_id:
                    round_lock_keys = [
                        f"round:{current_round_id}:buzzer_timer:lock",
                        f"round:{current_round_id}:buzzer_answer_timer:lock",
                        f"round:{current_round_id}:teamplay_timer:lock",
                    ]
                    await self.app.cache.pool.delete(*round_lock_keys)

                await self.app.game_service.update_state(
                    game_id, chat_id, message_id
                )

            offset += self.BATCH_SIZE
            await asyncio.sleep(0)
