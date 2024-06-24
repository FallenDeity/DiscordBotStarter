import datetime
import uuid

import attrs

__all__: tuple[str, ...] = (
    "Record",
    "Config",
)


class Record:
    """A record in the database."""


@attrs.define(frozen=True)
class Config(Record):
    """A record in the config table."""

    bot_id: int
    migrations: list["uuid.UUID"]
    last_login: datetime.datetime
