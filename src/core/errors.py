import datetime
import enum
import random
import typing as t

import attrs
import disnake
import humanfriendly
from disnake import Forbidden, NotFound
from disnake.ext import commands

__all__: tuple[str, ...] = (
    "BotExceptions",
    "MissingEnvironmentVariable",
    "ConversionError",
    "DateConversionError",
    "UknownError",
    "ViewException",
    "ExceptionResponse",
    "SpamGuilds",
    "DeveloperOnly",
    "DurationError",
    "ModalException",
    "ViewTimeout",
)


@attrs.define(kw_only=True, slots=True)
class ExceptionResponse:
    error: t.Type[Exception]
    messages: list[str]
    custom_error: bool = False

    @property
    def message(self) -> str:
        return random.choice(self.messages)


class TemplateException(commands.CommandError):
    ...


class ViewTimeout(TemplateException):
    def __init__(self) -> None:
        super().__init__("The view has timed out.")


class ModalException(TemplateException):
    def __init__(self, error: Exception, interaction: disnake.ModalInteraction) -> None:
        self.error = error
        self.interaction = interaction
        super().__init__(f"Failed to handle modal interaction {interaction}: {error}")

    def __str__(self) -> str:
        return (
            "Sorry but something went wrong. I have notified the developers about this issue."
            " Please try again later."
        )


class UknownError(TemplateException):
    """An unknown error occurred."""

    def __init__(self, error: Exception) -> None:
        self.error = error

    def __str__(self) -> str:
        return f"An unknown error occurred: {self.error}"


class DeveloperOnly(TemplateException):
    def __str__(self) -> str:
        return "This command can only be used by developers. How did you get here?"


class MissingEnvironmentVariable(TemplateException):
    """Exception raised when a required environment variable is missing."""

    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f"Missing environment variable: {name}")

    def __str__(self) -> str:
        return f"Missing environment variable: {self.name}"


class ConversionError(TemplateException):
    """Exception raised when a conversion fails."""

    def __init__(self, name: str, value: t.Any, error: Exception) -> None:
        self.name = name
        self.value = value
        self.error = error
        super().__init__(f"Failed to convert {name} to {value}: {error}")

    def __str__(self) -> str:
        return f"Failed to convert {self.name} to {self.value}: {self.error}"


class DateConversionError(ConversionError):
    """Exception raised when a date conversion fails."""

    def __init__(self, value: t.Any, error: Exception) -> None:
        super().__init__("date", value, error)

    def __str__(self) -> str:
        return f"Failed to convert {self.value} to a date: {self.error}"


class ViewException(TemplateException):
    """Exception raised when a view fails."""

    def __init__(
        self,
        error: Exception,
        item: disnake.ui.Item[disnake.ui.View],
        interaction: disnake.MessageInteraction,
    ) -> None:
        self.error = error
        self.item = item
        self.interaction = interaction
        super().__init__(f"Failed to handle view item {item} in interaction {interaction}: {error}")

    def __str__(self) -> str:
        return (
            "Sorry but something went wrong. I have notified the developers about this issue."
            " Please try again later."
        )


class SpamGuilds(TemplateException):
    """Exception raised when a user invites the bot to a spam guild."""

    THRESHOLD = 20
    BOT_THRESHOLD = 0.5

    def __init__(self, guild: disnake.Guild) -> None:
        self.guild = guild
        super().__init__(f"Spam guild: {guild}")

    def __str__(self) -> str:
        return (
            f"Sorry, but I cannot join {self.guild} because it is a spam guild."
            f" There needs to at least be {self.THRESHOLD} members in the guild."
        )


class DurationError(TemplateException):
    def __init__(self, message: str, duration: datetime.timedelta) -> None:
        self.message = message
        self.duration = duration
        super().__init__(f"Invalid duration: {duration} ({message})")

    def __str__(self) -> str:
        return f"Sorry, but the duration `{humanfriendly.format_timespan(self.duration)}` is invalid. {self.message}"


class BotExceptions(enum.Enum):
    MISSING_PERMISSIONS = ExceptionResponse(
        error=commands.MissingPermissions,
        messages=[
            "You need the following permission(s) to use this command:\n\
`{missing_perms}`",
            "Fam I'm sorry but this is the list of things you need for me to let you do this:\n{missing_perms}",
        ],
    )
    COOLDOWN = ExceptionResponse(
        error=commands.CommandOnCooldown,
        messages=[
            "The command is on cooldown! Try again in {retry_after} seconds.",
            "Hold your horses cowboy! Let me catch my breath, try again in {retry_after} seconds",
            "For the next {retry_after} seconds, how about you try relax and train your patience?",
        ],
    )
    MEMBER_NOT_FOUND = ExceptionResponse(
        error=commands.MemberNotFound,
        messages=[
            "Member '{error.argument}' does not exist.",
            "I'm sorry fam but {error.argument} might have catfished you cause i can't find this human",
            "You sure this person exists? Cause i can't seem to find this {error.argument} person you speak of",
            "That {error.argument} person might be a member of the Doe family cause I can't find 'em",
        ],
    )
    USER_NOT_FOUND = ExceptionResponse(
        error=commands.UserNotFound,
        messages=[
            "User '{error.argument}' does not exist.",
            "I'm sorry I tried my best but, alas, {error.argument} has escaped my clutches."
            "User {error.argument} might be the best hide and seek player, well at least they can hide from me.",
        ],
    )
    CHANNEL_NOT_FOUND = ExceptionResponse(
        error=commands.ChannelNotFound,
        messages=[
            "Channel '{error.argument}' does not exist.",
            "{error.argument} may be a road runner cause he pulled a fast one on me",
            "I don't know what universe you think {error.argument} exists in but, it's definitely not here",
        ],
    )
    ROLE_NOT_FOUND = ExceptionResponse(
        error=commands.RoleNotFound,
        messages=[
            "Role '{error.argument}' does not exist.",
            "I might be blind or stupid but I don't see a role named {error.argument} anywhere",
            "Who keeps giving me roles that don't exists???",
        ],
    )
    BOT_MISSING_PERMISSIONS = ExceptionResponse(
        error=commands.BotMissingPermissions,
        messages=[
            "Bot needs the following permission(s) to perform this command:\n\
`{missing_perms}`",
            "Sorry mate I can't do this without these permissions:\n{missing_perms}",
            "You sure i'm allowed to do this? Cause it seems like I don't have these permissions:\n{missing_perms}",
        ],
    )
    NOTFOUND = ExceptionResponse(
        error=NotFound,
        messages=[
            "Bot was unable to locate required message",
            "Sorry dam but I can't look for things that don't exist",
            "I searched the entire universe and still can't find that message",
        ],
    )
    FORBIDDEN = ExceptionResponse(
        error=Forbidden,
        messages=[
            "Bot does not have permission to do this. It is probably missing one of required permissions, "
            "check that the bot has all required permissions in this channel"
        ],
    )
    UKNOWN = ExceptionResponse(
        error=UknownError,
        messages=[
            "Sorry but something went wrong and I don't know what it is. I have notified my developers about this.",
            "I'm sorry but I don't know what happened. I have notified my developers about this.",
            "I don't know what happened but I have notified my developers about this.",
        ],
    )
    DateConversionError = ExceptionResponse(
        error=DateConversionError,
        messages=[],
        custom_error=True,
    )
    ViewException = ExceptionResponse(
        error=ViewException,
        messages=[],
        custom_error=True,
    )
    SpamGuilds = ExceptionResponse(
        error=SpamGuilds,
        messages=[],
        custom_error=True,
    )
    DeveloperOnly = ExceptionResponse(
        error=DeveloperOnly,
        messages=[],
        custom_error=True,
    )
    BadArgument = ExceptionResponse(
        error=commands.BadArgument,
        messages=[],
        custom_error=True,
    )
    DurationError = ExceptionResponse(
        error=DurationError,
        messages=[],
        custom_error=True,
    )
    ViewTimeout = ExceptionResponse(
        error=ViewTimeout,
        messages=[],
        custom_error=True,
    )

    @classmethod
    def get_response(cls, error: Exception) -> str | ExceptionResponse:
        for response in cls:
            if isinstance(error, response.value.error):
                if response.value.custom_error:
                    return str(error)
                response = response.value.message
                retry_after = int(getattr(error, "retry_after", 0))
                formatted_after = humanfriendly.format_timespan(retry_after) if retry_after else 0
                missing_perms = ", ".join([str(x) for x in getattr(error, "missing_permissions", [])])
                missing_roles = ", ".join([str(x) for x in getattr(error, "missing_roles", [])])
                return response.format(
                    error=error,
                    retry_after=formatted_after,
                    missing_perms=missing_perms,
                    missing_roles=missing_roles,
                )
        return cls.UKNOWN.value
