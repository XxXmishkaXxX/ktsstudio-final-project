from app.games.models.teams import Team, TeamMember
from app.store.base.accessor import BaseAccessor
from sqlalchemy import select
from sqlalchemy.orm import selectinload


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
