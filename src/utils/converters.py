import datetime
import typing as t

import disnake
from disnake.ext import commands
from durations_nlp import Duration

__all__: tuple[str, ...] = ("DurationConverter",)


class DurationConverter(commands.Converter[datetime.timedelta]):
    async def convert(
        self, ctx: commands.Context[t.Any] | disnake.ApplicationCommandInteraction, argument: str
    ) -> datetime.timedelta:
        try:
            return datetime.timedelta(seconds=Duration(argument).to_seconds())
        except ValueError:
            raise commands.BadArgument(f"{argument} is not a valid duration.")
