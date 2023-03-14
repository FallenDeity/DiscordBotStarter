import datetime
import typing as t

from src.database.models import Config as ConfigModel

from ._table import Table

if t.TYPE_CHECKING:
    import uuid


__all__: tuple[str, ...] = ("Config",)


class Config(Table):
    async def setup(self) -> None:
        await self.db.execute(
            "CREATE TABLE IF NOT EXISTS config "
            "(bot_id BIGINT,"
            " generation INT,"
            " migrations UUID [],"
            " quests TIMESTAMP,"
            " last_login TIMESTAMP,"
            " leaderboard TIMESTAMP,"
            " PRIMARY KEY (bot_id))"
        )

    async def get_config(self, bot_id: int) -> ConfigModel:
        data = await self.db.fetchrow("SELECT * FROM config WHERE bot_id = $1", bot_id)
        if data is None:
            stamp = datetime.datetime.now()
            ids: list["uuid.UUID"] = []
            args = (bot_id, 1, ids, stamp, stamp, stamp)
            await self.db.execute(
                "INSERT INTO config (bot_id, generation, migrations, quests, last_login, leaderboard) "
                "VALUES ($1, $2, $3, $4, $5, $6)",
                *args,
            )
            return ConfigModel(*args)
        return ConfigModel(*data)

    async def update_migration(self, bot_id: int, migration: "uuid.UUID") -> None:
        await self.db.execute(
            "UPDATE config SET migrations = array_append(migrations, $1) WHERE bot_id = $2",
            migration,
            bot_id,
        )

    async def update_login(self, bot_id: int) -> None:
        await self.db.execute(
            "UPDATE config SET last_login = $1 WHERE bot_id = $2",
            datetime.datetime.now(),
            bot_id,
        )

    async def update_leaderboard(self, bot_id: int) -> None:
        await self.db.execute(
            "UPDATE config SET leaderboard = $1 WHERE bot_id = $2",
            datetime.datetime.now(),
            bot_id,
        )

    async def update_quests(self, bot_id: int) -> None:
        await self.db.execute(
            "UPDATE config SET quests = $1 WHERE bot_id = $2",
            datetime.datetime.now(),
            bot_id,
        )
