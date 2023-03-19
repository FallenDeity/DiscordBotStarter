# pyright: reportUnknownVariableType=false

import importlib
import inspect
import time
import typing as t
import uuid

import asyncpg

from src.utils.constants import BOT_ID, PATHS

from .tables import Table

if t.TYPE_CHECKING:
    from src import TemplateBot

    from .tables import Config, Tickets


__all__: tuple[str, ...] = ("Database",)


class Database:
    _pool: asyncpg.Pool | None = None  # type: ignore[reportMissingTypeArgument]
    config: "Config"
    tickets: "Tickets"

    def __init__(self, bot: "TemplateBot") -> None:
        self.bot = bot

    async def _create_pool(self) -> None:
        self._pool = await asyncpg.create_pool(self.bot.config.PGURL)

    async def setup(self) -> None:
        self.bot.logger.info("Setting up the database...")
        await self._create_pool()
        await self._setup_extensions()
        await self._apply_migrations()
        await self.config.update_login(BOT_ID)
        self.bot.logger.info("Connected to the database.")

    async def close(self) -> None:
        assert self._pool is not None
        self.bot.logger.info("Closing the database connection...")
        await self._pool.close()

    async def _setup_extensions(self) -> None:
        self.bot.logger.flair("Setting up the database extensions...")
        extensions = PATHS.TABLES
        for file in extensions.glob("*.py"):
            if file.name.startswith("_"):
                continue
            module = importlib.import_module(
                f"{extensions.parent.as_posix().replace('/', '.')}.{extensions.name}.{file.stem}"
            )
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, Table) and name != "Table":
                    table = obj(self)
                    setattr(self, name.lower(), table)
                    await table.setup()
                    self.bot.logger.info(f"Loaded table {name}.")
        self.bot.logger.flair("Finished setting up the database extensions.")

    async def _apply_migrations(self) -> None:
        assert self._pool is not None
        bot_config = await self.config.get_config(BOT_ID)
        migrations = PATHS.MIGRATIONS
        updates: dict[str, float] = {}
        applied = {str(m) for m in bot_config.migrations}
        for file in migrations.glob("*.sql"):
            ts = float(file.name.split("-")[0])
            name = file.name.replace(".sql", "").replace(f"{ts}-", "")
            if name not in applied:
                updates[name] = ts
        unapplied = set(updates.keys()) - applied
        if not unapplied:
            self.bot.logger.info("No migrations to apply.")
            return
        self.bot.logger.warning(f"Applying {len(unapplied)} migrations...")
        ordered = sorted(unapplied, key=lambda x: updates[x])
        for migration in ordered:
            path = migrations / f"{updates[migration]}-{migration}.sql"
            try:
                self.bot.logger.info(f"Applying migration {migration}...")
                await self._pool.execute(path.read_text())
                await self.config.update_migration(BOT_ID, uuid.UUID(migration))
                self.bot.logger.info(f"Applied migration {migration}.")
            except Exception as e:
                self.bot.logger.critical(f"Failed to apply migration {migration}! Rolling back...")
                raise e
        self.bot.logger.flair("Finished applying migrations.")

    async def execute(self, query: str, *args: t.Any) -> None:
        assert self._pool is not None
        async with self._pool.acquire() as conn:
            await conn.execute(query, *args)

    async def fetch(self, query: str, *args: t.Any) -> t.Any:
        assert self._pool is not None
        async with self._pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args: t.Any) -> t.Any:
        assert self._pool is not None
        async with self._pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def execute_many(self, query: str, *args: t.Any) -> None:
        assert self._pool is not None
        async with self._pool.acquire() as conn:
            await conn.executemany(query, *args)

    async def fetchval(self, query: str, *args: t.Any) -> t.Any:
        assert self._pool is not None
        async with self._pool.acquire() as conn:
            return await conn.fetchval(query, *args)

    async def ping(self) -> float:
        assert self._pool is not None
        async with self._pool.acquire() as conn:
            start = time.perf_counter()
            await conn.execute("SELECT 1")
            return time.perf_counter() - start
