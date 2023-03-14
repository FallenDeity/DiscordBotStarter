import datetime
import uuid

import attrs

__all__: tuple[str, ...] = (
    "Record",
    "Config",
    "TicketSystem",
)


class Record:
    """A record in the database."""


@attrs.define(frozen=True)
class Config(Record):
    """A record in the config table."""

    bot_id: int
    generation: int
    migrations: list["uuid.UUID"]
    quests: datetime.datetime
    last_login: datetime.datetime
    leaderboard: datetime.datetime


@attrs.define(frozen=True)
class TicketSystem(Record):
    """A ticket system record."""

    guild_id: int
    channel_id: int
    archive_channel_id: int
    roles: list[int]
