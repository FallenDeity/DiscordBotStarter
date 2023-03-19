import difflib
import itertools
import random
import typing as t

import disnake
from disnake.ext import commands, tasks

from src.core.errors import BotExceptions, DeveloperOnly, ExceptionResponse, SpamGuilds
from src.core.views.paginators import ClassicPaginator
from src.core.views.url_buttons import invite_buttons_view
from src.utils.ansi import Colors
from src.utils.constants import CHANNELS, DEVELOPERS, GUILD_ID
from src.utils.eval import Eval

from . import BaseCog

if t.TYPE_CHECKING:
    from src import TemplateBot


class System(BaseCog):
    """
    Cog containing system commands and bot events for developer use only.
    """

    _log_channel: disnake.TextChannel | None = None
    _activity_message = itertools.cycle(
        (
            "{guilds:,} servers",
            "{users:,} users",
        )
    )
    _error_titles: tuple[str, ...] = (
        "Oops! Something went wrong.",
        "Oh no! An error occurred.",
        "Sorry, an error occurred.",
        "Whoops, there was a problem.",
        "Oof, an error has occurred.",
        "Yikes, something went wrong.",
        "Bummer, there was a problem.",
        "Shoot, something went wrong.",
    )
    spam_check: bool = False

    def __init__(self, bot: "TemplateBot") -> None:
        super().__init__(bot)
        self._update_status.start()

    @tasks.loop(seconds=10)
    async def _update_status(self) -> None:
        await self.bot.wait_until_ready()
        message = next(self._activity_message).format(guilds=len(self.bot.guilds), users=len(self.bot.users))
        await self.bot.change_presence(
            activity=disnake.Activity(
                name=f"{message} | Use /help",
                type=disnake.ActivityType.watching,
            )
        )

    async def _load_channel(self) -> disnake.TextChannel:
        if self._log_channel is None:
            channel = self.bot.get_channel(CHANNELS.LOGS) or await self.bot.fetch_channel(CHANNELS.LOGS)
            assert isinstance(channel, disnake.TextChannel)
            self._log_channel = channel
        return self._log_channel

    @staticmethod
    async def _dev_check(inter: disnake.Interaction) -> bool:
        if inter.user.id not in DEVELOPERS:
            raise DeveloperOnly()
        return True

    async def cog_message_command_check(self, inter: disnake.ApplicationCommandInteraction) -> bool:  # type: ignore
        return bool(await self._dev_check(inter))

    async def cog_slash_command_check(self, inter: disnake.ApplicationCommandInteraction) -> bool:  # type: ignore
        return bool(await self._dev_check(inter))

    @commands.Cog.listener(disnake.Event.user_command_error)
    @commands.Cog.listener(disnake.Event.slash_command_error)
    @commands.Cog.listener(disnake.Event.message_command_error)
    async def handle_error(self, inter: disnake.ApplicationCommandInteraction, error: commands.CommandError) -> None:
        if not isinstance(error, commands.CommandOnCooldown):
            inter.application_command.reset_cooldown(inter)
        error_data = BotExceptions.get_response(error)
        title = random.choice(self._error_titles)
        if error_data is BotExceptions.UKNOWN.value:
            assert isinstance(error_data, ExceptionResponse)
            desc = self.bot.embeds.ansi(str(error_data.message), Colors.RED)
            await inter.edit_original_message(
                embed=disnake.Embed(title=title, description=desc, color=disnake.Color.red())
            )
            raise error
        desc = self.bot.embeds.ansi(str(error_data), Colors.RED)
        await inter.edit_original_message(
            embed=disnake.Embed(title=title, description=desc, colour=disnake.Color.red())
        )

    @commands.Cog.listener()
    async def on_guild_join(self, guild: disnake.Guild) -> None:
        channel = await self._load_channel()
        members = len(guild.members)
        bots = sum(1 for member in guild.members if member.bot)
        common_channel_names = ["general", "lounge", "chat", "welcome"]
        cperms = list(filter(lambda x: x.permissions_for(guild.me).send_messages, guild.text_channels))
        cnames = difflib.get_close_matches([c.name for c in cperms], common_channel_names)
        channels = [c for c in cperms if c.name in cnames] + [c for c in cperms if c.name not in cnames]
        if (SpamGuilds.THRESHOLD > members or (bots / members) >= SpamGuilds.BOT_THRESHOLD) and self.spam_check:
            if channels:
                await channels[0].send(embed=self.bot.embeds.spam_guild(guild))
            await guild.leave()
            raise SpamGuilds(guild)
        self.bot.logger.info(f"Joined guild {guild} with {members} members.")
        if channels:
            await channels[0].send(
                embed=self.bot.embeds.welcome_embed(guild),
                view=invite_buttons_view(self.bot),
            )
        else:
            self.bot.logger.warning(
                f"Unable to find a channel to send the welcome message in {guild.name} ({guild.id})"
            )
        await channel.send(embed=self.bot.embeds.log_guild_join(guild))

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: disnake.Guild) -> None:
        channel = await self._load_channel()
        self.bot.logger.info(f"Left guild {guild} with {len(guild.members)} members.")
        await channel.send(embed=self.bot.embeds.log_guild_leave(guild))

    @commands.message_command(
        name="Execute Code",
        description="Execute a python code",
        guild_ids=[GUILD_ID],
    )
    async def exec(self, inter: disnake.ApplicationCommandInteraction, message: disnake.Message) -> None:
        """
        Execute a python code.

        Parameters
        ----------
        inter : disnake.ApplicationCommandInteraction
            The interaction that invoked the command
        message : disnake.Message
            The message containing the code to execute
        """
        code = message.content
        code = code.replace("```py", "").replace("```", "").strip()
        evaluator = Eval()
        renv = {"bot": self.bot, "inter": inter}
        stdout, stderr = await evaluator.f_eval(code=code, renv=renv)
        embeds = self.bot.embeds.build_error_embed("Code Execution", stdout + stderr)
        await ClassicPaginator.start(inter, items=list(embeds), timeout=60)
