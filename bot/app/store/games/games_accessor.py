from app.games.models.games import Game, GameState
from app.store.base.accessor import BaseAccessor
from sqlalchemy import select


class GameAccessor(BaseAccessor):
    async def create_game(self, chat_id: int) -> Game:
        async with self.app.database.session() as session:
            game = Game(chat_id=chat_id, state=GameState.created)
            session.add(game)
            await session.commit()
            await session.refresh(game)
            return game

    async def is_active_game_in_chat(self, chat_id: int) -> Game | None:
        async with self.app.database.session() as session:
            game = (
                await session.execute(
                    select(Game).where(
                        Game.chat_id == chat_id
                        and Game.state != GameState.finished
                    )
                )
            ).scalar_one_or_none()
            return bool(game)

    async def get_game_by_id(self, game_id: int) -> Game | None:
        async with self.app.database.session() as session:
            result = await session.execute(
                select(Game).where(Game.id == game_id)
            )
            return result.scalar_one_or_none()

    async def get_game_state(self, game_id: int):
        async with self.app.database.session() as session:
            return (
                await session.execute(
                    select(Game.state).where(Game.id == game_id)
                )
            ).scalar_one()
