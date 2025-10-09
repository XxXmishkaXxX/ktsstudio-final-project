from shared_models.games import Game, GameState
from app.store.base.accessor import BaseAccessor
from sqlalchemy import and_, select, update


class GameAccessor(BaseAccessor):
    async def create_game(self, chat_id: int) -> Game:
        async with self.app.database.session() as session:
            game = Game(chat_id=chat_id, state=GameState.created)
            session.add(game)
            await session.commit()
            await session.refresh(game)
            return game

    async def delete_game(self, game_id: int):
        async with self.app.database.session() as session:
            result = await session.execute(
                select(Game).where(Game.id == game_id)
            )
            game = result.scalars().first()
            if game:
                await session.delete(game)
                await session.commit()

    async def is_active_game_in_chat(self, chat_id: int) -> Game | None:
        async with self.app.database.session() as session:
            return (
                await session.execute(
                    select(Game).where(
                        and_(
                            Game.chat_id == chat_id,
                            Game.state != GameState.finished,
                        )
                    )
                )
            ).scalar_one_or_none()

    async def get_game_by_id(self, game_id: int) -> Game | None:
        async with self.app.database.session() as session:
            result = await session.execute(
                select(Game).where(Game.id == game_id)
            )
            return result.scalar_one_or_none()

    async def get_game_by_chat_id(self, chat_id: int) -> Game | None:
        async with self.app.database.session() as session:
            result = await session.execute(
                select(Game).where(Game.chat_id == chat_id)
            )
            return result.scalar_one_or_none()

    async def get_game_state(self, game_id: int):
        async with self.app.database.session() as session:
            return (
                await session.execute(
                    select(Game.state).where(Game.id == game_id)
                )
            ).scalar_one()

    async def set_game_state(self, game_id: int, state: GameState):
        async with self.app.database.session() as session:
            await session.execute(
                update(Game).where(Game.id == game_id).values(state=state.value)
            )
            await session.commit()

    async def get_games_by_states(
        self,
        states: list[GameState],
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Game]:
        if not states:
            return []

        states_values = [state.value for state in states]

        async with self.app.database.session() as session:
            query = select(Game).where(Game.state.in_(states_values))
            if limit is not None:
                query = query.limit(limit)
            if offset is not None:
                query = query.offset(offset)

            result = await session.execute(query)
            return result.scalars().all()

    async def get_current_round_id(self, game_id: int):
        async with self.app.database.session() as session:
            return (
                await session.execute(
                    select(Game.current_round_id).where(Game.id == game_id)
                )
            ).scalar_one_or_none()
