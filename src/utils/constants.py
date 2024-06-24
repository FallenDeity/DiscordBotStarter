import enum
import typing as t

import attrs

__all__: tuple[str, ...] = (
    "CHANNELS",
    "PATHS",
    "DEVELOPERS",
    "EMOJIS",
    "GUILD_ID",
    "BOT_ID",
    "ERRORS",
)


ERRORS: tuple[str, ...] = (
    "Oops! Something went wrong.",
    "Oh no! An error occurred.",
    "Sorry, an error occurred.",
    "Whoops, there was a problem.",
    "Oof, an error has occurred.",
    "Yikes, something went wrong.",
    "Bummer, there was a problem.",
    "Shoot, something went wrong.",
)

T = t.TypeVar("T")


class BaseEnum(enum.Enum):
    def __get__(self, *_: t.Any) -> t.Any:
        return self.value


@attrs.define(repr=False, slots=True, kw_only=True)
class Emoji:
    id: int
    name: str
    animated: bool = False

    def __repr__(self) -> str:
        animated = "a" if self.animated else ""
        return f"<{animated}:_:{self.id}>"


DEVELOPERS: set[int] = {656838010532265994, 923636820019916850}
GUILD_ID: int = 1254711706157060146
BOT_ID: int = 1254713762720645170


class CHANNELS(enum.IntEnum):
    LOGS = 1085144172064948285


class PATHS(str, BaseEnum):
    BASE = "src"
    BIN = "src/bin"
    DATABASE = "src/database"
    EXTENSIONS = "src/ext"
    MIGRATIONS = "src/bin/migrations"
    TABLES = "src/database/tables"


class EMOJIS(BaseEnum):
    def __get__(self, *_: t.Any) -> Emoji:
        return self.value
