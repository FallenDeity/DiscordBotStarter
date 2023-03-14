import dataclasses
import typing

import disnake
from disnake.ext import commands

from src.core.views.paginators import ClassicPaginator, MenuPaginator

from .ansi import AnsiBuilder, Colors, Styles
from .embeds import BaseEmbed

if typing.TYPE_CHECKING:
    from src import TemplateBot


IGNORED_COGS: tuple[str, ...] = ("System",)


@dataclasses.dataclass(kw_only=True)
class Help:
    interaction: disnake.ApplicationCommandInteraction
    argument: str | None

    @property
    def bot(self) -> "TemplateBot":
        return typing.cast("TemplateBot", self.interaction.client)

    def create_cog_help(self, cog: commands.Cog) -> list[BaseEmbed]:
        desc = AnsiBuilder.from_string_to_ansi(
            cog.description or "No description provided for category",
            Styles.BOLD,
            Colors.BLUE,
        )
        embeds: list[BaseEmbed] = []
        page_commands = [
            cog.get_slash_commands()[x : x + 100]
            for x in range(0, len(cog.get_slash_commands()), 100)
        ]
        for page in page_commands:
            txt = ""
            for command in page:
                global_cmd = self.bot.get_global_command_named(command.name)
                assert global_cmd is not None
                txt += (
                    f"- **</{global_cmd.name}:{global_cmd.id}>**\n"
                    f"{AnsiBuilder.from_string_to_ansi(command.description, Colors.GREEN)}\n"
                )
            embeds.append(
                BaseEmbed(
                    description=f"{desc}\n**Commands Info.**\n{txt}",
                    color=disnake.Color.blue(),
                    user=self.interaction.user,
                ).set_author(
                    name=f"{cog.qualified_name.title()} Commands",
                    icon_url=self.bot.user.display_avatar,
                )
            )

        return embeds

    def get_usual_buttons(self) -> list[disnake.ui.Button[None]]:
        return [
            disnake.ui.Button(style=disnake.ButtonStyle.link, label=label, url=url)
            for label, url in {
                "Invite Bot": self.bot.invite_url,
                "Support Server": self.bot.server_url,
            }.items()
        ]

    async def send_help(self) -> None:
        if self.argument is None:
            await self.send_bot_help()
        elif (cog := self.bot.get_cog(self.argument)) is not None:
            await self.send_cog_help(
                cog
            ) if cog.qualified_name not in IGNORED_COGS else None
            return
        elif (command := self.bot.get_slash_command(self.argument)) is not None:
            if isinstance(command, commands.InvokableSlashCommand):
                await self.send_command_help(command)
            elif isinstance(command, commands.SubCommandGroup):
                await self.send_group_help(command)
            else:
                await self.send_sub_command_group(command)
        else:
            await self.invalid_help_object()

    async def invalid_help_object(self) -> None:
        await self.interaction.send(
            embed=BaseEmbed(
                description=f"`{self.argument}` is an invalid help argument.",
                user=self.interaction.user,
            )
        )

    async def send_bot_help(self) -> None:
        assert (bot_user := self.bot.user) is not None
        assert isinstance(user := self.interaction.user, disnake.Member)
        embed = BaseEmbed(
            user=user,
            color=disnake.Color.green(),
            description="**Welcome to the help menu!**",
        ).set_thumbnail(bot_user.display_avatar)
        selectors: dict[str, list[BaseEmbed]] = {}
        for cog in self.bot.cogs.values():
            if cog.qualified_name in IGNORED_COGS:
                continue
            txt = AnsiBuilder.from_string_to_ansi(
                ", ".join(command.name for command in cog.get_slash_commands()),
                Colors.YELLOW,
            )
            embed.add_field(cog.qualified_name + " Commands", txt, inline=False)
            selectors[cog.qualified_name] = self.create_cog_help(cog)
        view = MenuPaginator(user, items={"Home": [embed]} | selectors)
        [view.add_item(comp) for comp in self.get_usual_buttons()]
        await self.interaction.send(embed=embed, view=view)
        view.message = await self.interaction.original_response()

    async def send_command_help(
        self, command: commands.InvokableSlashCommand | commands.SubCommand
    ) -> None:
        embed = (
            BaseEmbed(color=disnake.Color.green(), user=self.interaction.user)
            .set_author(name=f"{command.name.title()} Command")
            .add_footer(text=f"Requested by: {self.interaction.user}")
            .set_thumbnail(self.bot.user.display_avatar)
        )

        embed.description = AnsiBuilder.from_string_to_ansi(
            command.description or "No description provided", Colors.BLUE
        )
        if (
            isinstance(command, commands.InvokableSlashCommand)
            and (o := command.options)
        ) or (
            isinstance(command, commands.SubCommand) and (o := command.option.options)
        ):
            txt = " ".join(
                AnsiBuilder.from_string_to_ansi(
                    arg.name + ": ", Colors.RED, Styles.BOLD
                )
                + AnsiBuilder.from_string_to_ansi(
                    arg.description.replace("-", "") or "No description", Colors.YELLOW
                )
                for arg in o
            )
            embed.description += "**Command Arguments:**\n" + txt
        await self.interaction.send(embed=embed)

    async def send_group_help(self, group: commands.SubCommandGroup) -> None:
        embed = BaseEmbed(color=disnake.Color.green(), user=self.interaction.user)
        embed.description = (
            AnsiBuilder.from_string_to_ansi(group.option.description, Colors.BLUE)
            + " **Subcommands:**\n"
        )
        txt = ""
        for command in group.children.values():
            txt += (
                AnsiBuilder.from_string_to_ansi(
                    command.name + ": ", Colors.RED, Styles.BOLD
                )
                + AnsiBuilder.from_string_to_ansi(command.description, Colors.YELLOW)
                + "\n"
            )
        embed.description += txt

    async def send_sub_command_group(self, command: commands.SubCommand) -> None:
        await self.send_command_help(command)

    async def send_cog_help(self, cog: commands.Cog) -> None:
        embeds = self.create_cog_help(cog)
        assert isinstance(user := self.interaction.user, disnake.Member)
        view = ClassicPaginator(
            user,
            items=embeds,
        )
        [view.add_item(comp) for comp in self.get_usual_buttons()]
        await self.interaction.send(embed=embeds[0], view=view)
