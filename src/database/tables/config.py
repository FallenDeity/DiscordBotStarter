import datetime
import typing as t

from src.database.models import Config as ConfigModel

from ._table import Table

if t.TYPE_CHECKING:
    import uuid


__all__: tuple[str, ...] = ("Config",)


class Config(Table[ConfigModel]):
    async def setup(self) -> None:
        await self.db.execute(
            "CREATE TABLE IF NOT EXISTS config "
            "(bot_id BIGINT,"
            " migrations UUID [],"
            " last_login TIMESTAMP,"
            " PRIMARY KEY (bot_id))"
        )

    async def get(self, id: int) -> ConfigModel:
        data = await self.db.fetchrow("SELECT * FROM config WHERE bot_id = $1", id)
        if data is None:
            config = ConfigModel(id, [], datetime.datetime.now())
            await self.create(config)
            return config
        return ConfigModel(*data)

    async def update(self, record: ConfigModel) -> None:
        await self.db.execute(
            "UPDATE config SET migrations = $1, last_login = $2 WHERE bot_id = $3",
            record.migrations,
            record.last_login,
            record.bot_id,
        )

    async def delete(self, record: ConfigModel) -> None:
        await self.db.execute("DELETE FROM config WHERE bot_id = $1", record.bot_id)

    async def get_all(self) -> list[ConfigModel]:
        data = await self.db.fetch("SELECT * FROM config")
        return [ConfigModel(*record) for record in data]

    async def create(self, record: ConfigModel) -> None:
        await self.db.execute(
            "INSERT INTO config (bot_id, migrations, last_login) VALUES ($1, $2, $3)",
            record.bot_id,
            record.migrations,
            record.last_login,
        )

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
