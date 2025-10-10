from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from db_core.models.teams import Team, TeamMember

from .base import BaseAccessor


class TeamAccessor(BaseAccessor):
    async def create_team(self, game_id: int) -> Team:
        async with self.app.database.session() as session:
            team = Team(game_id=game_id)
            session.add(team)
            await session.commit()
        return team

    async def get_game_teams(self, game_id: int):
        async with self.app.database.session() as session:
            result = await session.execute(
                select(Team)
                .options(
                    selectinload(Team.members).selectinload(TeamMember.user)
                )
                .where(Team.game_id == game_id)
            )
            return result.scalars().all()

    async def get_team_by_id(self, team_id: int):
        async with self.app.database.session() as session:
            return (
                await session.execute(
                    select(Team)
                    .options(selectinload(TeamMember.user_id))
                    .where(Team.id == team_id)
                )
            ).scalar_one_or_none()

    async def join_team(self, team_id: int, tg_id: int):
        async with self.app.database.session() as session:
            member = TeamMember(team_id=team_id, user_id=tg_id)
            session.add(member)
            await session.commit()

    async def leave_team(self, team_id: int, tg_id: int):
        async with self.app.database.session() as session:
            member = await session.execute(
                select(TeamMember).where(
                    TeamMember.team_id == team_id, TeamMember.user_id == tg_id
                )
            )
            member = member.scalars().first()
            if member:
                await session.delete(member)
                await session.commit()

    async def get_team_by_user_id(self, game_id: int, user_id: int):
        async with self.app.database.session() as session:
            result = await session.execute(
                select(Team.id)
                .join(TeamMember.team)
                .where(Team.game_id == game_id, TeamMember.user_id == user_id)
            )
            return result.scalar_one_or_none()

    async def add_team_score(self, team_id: int, score: int):
        async with self.app.database.session() as session:
            result = await session.execute(
                select(Team).where(Team.id == team_id)
            )
            team = result.scalar_one_or_none()

            if not team:
                raise ValueError("Команда не найдена")

            await session.execute(
                update(Team)
                .where(Team.id == team_id)
                .values(score=Team.score + score)
            )
            await session.commit()
