import io
import typing as t

import disnake

from src.core.errors import SpamGuilds

from .ansi import AnsiBuilder, BackgroundColors, Colors, Styles

if t.TYPE_CHECKING:
    from src import TemplateBot


__all__: tuple[str, ...] = (
    "Embeds",
    "BaseEmbed",
)
User = disnake.Member | disnake.User | disnake.ClientUser
Asset = disnake.Asset | str | None


class BaseEmbed(disnake.Embed):
    def __init__(
        self,
        *,
        user: User | None = None,
        raw: io.BytesIO | None = None,
        file: disnake.File | None = None,
        **kwargs: t.Any,
    ) -> None:
        super().__init__(**kwargs)
        self._file = file
        self._raw = raw
        self.user = user
        self.timestamp = disnake.utils.utcnow()

    def add_footer(self, *, text: str, icon_url: Asset = None) -> "BaseEmbed":
        text = f"{text} | {self.footer.text}" if self.footer.text else text
        icon_url = icon_url or self.footer.icon_url
        self.set_footer(text=text, icon_url=icon_url)
        return self

    def add_file(self, file: disnake.File) -> "BaseEmbed":
        self._raw = io.BytesIO(file.fp.read())
        self._raw.seek(0)
        self._file = disnake.File(self._raw, filename=file.filename)
        return self

    @property
    def file(self) -> disnake.File:
        assert self._file is not None, "No file attached to this embed."
        assert self._raw is not None, "No file attached to this embed."
        self._raw.seek(0)
        return disnake.File(self._raw, filename=self._file.filename)


class Embeds:
    def __init__(self, bot: "TemplateBot") -> None:
        self.bot = bot
        self.ansi = AnsiBuilder

    def yes_embed(self, title: str, description: str) -> BaseEmbed:
        embed = BaseEmbed(
            user=self.bot.user,
            title=title,
            description=description,
            color=disnake.Color.green(),
        )
        return embed

    def no_embed(self, title: str, description: str) -> BaseEmbed:
        embed = BaseEmbed(
            user=self.bot.user,
            title=title,
            description=description,
            color=disnake.Color.red(),
        )
        return embed

    def log_guild_join(self, guild: disnake.Guild) -> BaseEmbed:
        embed = BaseEmbed(
            user=self.bot.user,
            title="Joined a new guild!",
            description=self.ansi.from_string_to_ansi(
                f"{guild.name} ({guild.id})",
                Colors.GREEN,
                Styles.BOLD,
                BackgroundColors.FIREFLY_DARK_BLUE,
            ),
            color=disnake.Color.green(),
        )
        embed.add_field(
            name="Owner",
            value=self.ansi.from_string_to_ansi(f"{guild.owner} ({guild.owner_id})", Colors.RED),
            inline=True,
        )
        embed.add_field(
            name="Members",
            value=self.ansi.from_string_to_ansi(f"{guild.member_count}", Colors.MAGENTA),
            inline=True,
        )
        embed.add_field(
            name="Created at",
            value=self.ansi.from_string_to_ansi(f"{guild.created_at.strftime('%d/%m/%Y %H:%M:%S')}", Colors.CYAN),
            inline=True,
        )
        embed.set_thumbnail(url=guild.icon)
        return embed

    def log_guild_leave(self, guild: disnake.Guild) -> BaseEmbed:
        embed = self.log_guild_join(guild)
        embed.title = "Left a guild!"
        return embed

    def spam_guild(self, guild: disnake.Guild) -> BaseEmbed:
        text = f"Miniumum members: {SpamGuilds.THRESHOLD} | Bot threshold: {SpamGuilds.BOT_THRESHOLD}"
        embed = BaseEmbed(
            user=self.bot.user,
            title="🚫 Unauthorized guild",
            description=(
                "**This guild has been automatically removed from the bot because it is a spam guild.**\n"
                "\n*If you think this is a mistake, please contact the bot owner.*\n"
                f"\n{self.ansi.from_string_to_ansi(text, Colors.RED, Styles.BOLD)}\n"
                f"\n**👤 Members:** `{guild.member_count}` ◈ "
                f"**🤖 Bots:** `{sum(1 for member in guild.members if member.bot)}`"
            ),
            color=disnake.Color.red(),
        )
        return embed

    def welcome_embed(self, guild: disnake.Guild) -> BaseEmbed:
        embed = BaseEmbed(
            user=self.bot.user,
            title="Welcome to Template Bot!",
            description="""
                        Template Bot for ticket, moderation, fun, and more!
                        """,
            color=disnake.Color.yellow(),
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar)
        embed.add_footer(text=f"Thanks for adding me to {guild.name}!")
        return embed

    def build_error_embed(self, title: str, description: str) -> t.Sequence[BaseEmbed]:
        chunks: list[str] = []
        string: list[str] = []
        for line in description.splitlines():
            if sum(len(s) for s in string) + len(line) > 1024:
                chunks.append("\n".join(string))
                string.clear()
            string.append(line)
        if string:
            chunks.append("\n".join(string))
        if not chunks:
            chunks.append("No output.")
        return [
            BaseEmbed(
                user=self.bot.user,
                title=title,
                description=f"```py\n{chunk}```",
                color=disnake.Color.red(),
            )
            for chunk in chunks
        ]

    async def ping_embed(self) -> disnake.Embed:
        bot_ = self.ansi.from_string_to_ansi(f"Bot: {self.bot.latency * 1000:.2f}ms", Colors.CYAN, Styles.BOLD)
        db_ = self.ansi.from_string_to_ansi(
            f"Database: {await self.bot.db.ping()*1000:.2f}ms",
            Colors.MAGENTA,
            Styles.BOLD,
        )
        embed = disnake.Embed(
            title="🏓 Pong!",
            description=f"{bot_}{db_}",
            color=disnake.Color.green(),
        )
        embed.timestamp = disnake.utils.utcnow()
        embed.set_thumbnail(url=self.bot.user.display_avatar)
        return embed
