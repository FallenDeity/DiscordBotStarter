import datetime
import importlib
import inspect
import traceback
import typing as t

import aiohttp
import disnake
from disnake.ext import commands

from src.database import Database
from src.utils.constants import (CHANNELS, EMOJIS, GITHUB, INVITE, PATHS,
                                 WEBSITE)
from src.utils.embeds import Embeds

from .env import TEMPLATEENV
from .logger import Logger

__all__: tuple[str, ...] = ("TemplateBot",)


class TemplateBot(commands.InteractionBot):
    _uptime: datetime.datetime = datetime.datetime.utcnow()
    http_session: aiohttp.ClientSession
    __version__: str = "0.0.1"
    __author__: str = "FallenDeity"

    def __init__(self) -> None:
        intents = disnake.Intents(
            emojis=True,
            guild_messages=True,
            guild_scheduled_events=True,
            guild_typing=True,
            guilds=True,
            members=True,
        )
        self.db = Database(self)
        self.logger = Logger(name="TemplateBot")
        self.embeds = Embeds(self)
        self.config = TEMPLATEENV
        super().__init__(intents=intents)

    @staticmethod
    def emoji(name: str) -> str:
        emoji = getattr(EMOJIS, "".join(i for i in name.upper() if i.isalnum()), None)
        if emoji is None:
            emoji = "❓"
        return repr(emoji)

    def disable_dm_commands(self) -> None:
        for command in self.slash_commands:
            command.body.dm_permission = False

    async def log_error(self, message: str) -> None:
        tb = traceback.format_exc()
        self.logger.error(f"{message}\n{tb}")
        channel = self.get_channel(int(CHANNELS.LOGS)) or await self.fetch_channel(
            int(CHANNELS.LOGS)
        )
        try:
            assert isinstance(channel, disnake.TextChannel)
            embeds = self.embeds.build_error_embed(title=message, description=tb)
            await channel.send(embeds=list(embeds))
        except AssertionError:
            self.logger.error("The channel is not a text channel.")
        except Exception as e:
            self.logger.error(f"Failed to send the error log.\n{e}\n{tb}")

    async def on_error(
        self, event_method: str, *_args: t.Any, **_kwargs: t.Any
    ) -> None:
        await self.log_error(f"An error occurred in {event_method}.")

    def _auto_setup(self, path: str) -> None:
        module = importlib.import_module(path)
        for name, obj in inspect.getmembers(module):
            if (
                inspect.isclass(obj)
                and issubclass(obj, commands.Cog)
                and name != "BaseCog"
            ):
                self.add_cog(obj(self))
                self.logger.info(f"Loaded {name} cog.")

    def _load_all_extensions(self) -> None:
        self.logger.info("Loading extensions...")
        extensions = PATHS.EXTENSIONS
        for path in extensions.glob("*.py"):
            if path.name.startswith("_"):
                continue
            self._auto_setup(f"{extensions.parent}.{extensions.name}.{path.stem}")
        self.logger.info("Loaded all extensions!")

    async def close(self) -> None:
        self.logger.info("Closing...")
        await self.db.close()
        await super().close()
        self.logger.info("Closed!")

    async def on_ready(self) -> None:
        self.logger.flair(f"Logged in as {self.user} ({self.user.id})")

    async def on_application_command(
        self, interaction: disnake.ApplicationCommandInteraction
    ) -> None:
        await interaction.response.defer()
        await self.process_application_commands(interaction)

    def run(self, *args: t.Any, **kwargs: t.Any) -> None:
        self.http_session = aiohttp.ClientSession()
        self.loop.run_until_complete(self.db.setup())
        self._load_all_extensions()
        self.disable_dm_commands()
        self.logger.info("Starting...")
        try:
            super().run(str(self.config.TOKEN), *args, **kwargs)
        except (KeyboardInterrupt, KeyError):
            self.logger.critical("Failed to run the bot!")
            self.logger.info("Closed!")

    @property
    def user(self) -> disnake.ClientUser:
        assert super().user, "bot user not cached yet"
        return super().user

    @property
    def invite_url(self) -> str:
        return (
            f"https://discord.com/oauth2/authorize?client_id={self.user.id}"
            f"&scope=applications.commands%20bot&permissions=277025778760"
        )

    @property
    def uptime(self) -> float:
        return (datetime.datetime.utcnow() - self._uptime).total_seconds()

    @property
    def website_url(self) -> str:
        return WEBSITE or "https://example.com"

    @property
    def github_url(self) -> str:
        return GITHUB or "https://github.com/"

    @property
    def server_url(self) -> str:
        return f"https://discord.gg/{INVITE}"
