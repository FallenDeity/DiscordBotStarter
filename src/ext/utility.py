import typing

import disnake
from disnake.ext import commands

from src.core.views.url_buttons import invite_buttons_view
from src.utils.ansi import Colors, Styles
from src.utils.help import Help

from . import BaseCog

IGNORED_COGS: tuple[str, ...] = ("System",)


class Utility(BaseCog):
    """Utility commands for the bot displaying information about the bot."""

    @property
    def command_names(self) -> list[str]:
        all_commands: list[str] = []
        for command in self.bot.slash_commands:
            if command.cog_name in IGNORED_COGS:
                continue
            for subcommand in command.children.values():
                all_commands.append(subcommand.qualified_name)
            all_commands.append(command.qualified_name)
        return all_commands

    @commands.slash_command(
        name="help", description="Get help about a command or category."
    )
    async def help_command(
        self, inter: disnake.ApplicationCommandInteraction, argument: str | None = None
    ) -> None:
        """Get help about a command or category.

        Parameters
        ----------
        inter : disnake.ApplicationCommandInteraction
            The interaction that invoked this command.
        argument : str | None
            The command or category to get help about.
        """
        helper = Help(interaction=inter, argument=argument)
        await helper.send_help()

    @help_command.autocomplete("argument")
    async def help_ac(self, inter: disnake.CommandInteraction, arg: str) -> list[str]:
        bot = inter.bot
        _list = [
            cog
            for cog in bot.cogs
            if arg.lower() in cog.lower() and cog not in IGNORED_COGS
        ]
        _list.extend(self.command_names)
        return _list[:25]

    @commands.slash_command(
        name="clear", description="Clear a certain amount of messages."
    )
    async def clear_command(
        self,
        inter: disnake.ApplicationCommandInteraction,
        amount: commands.Range[1, 100],
    ) -> None:
        """Clear a certain amount of messages.

        Parameters
        ----------
        inter : disnake.ApplicationCommandInteraction
            The interaction that invoked this command.
        amount : int
            The amount of messages to clear.
        """
        await inter.channel.purge(limit=typing.cast(int, amount) + 1)
        embed = self.bot.embeds.yes_embed("Purged", f"Purged {amount} messages.")
        await inter.send(embed=embed, ephemeral=True)

    @commands.slash_command(name="ping")
    async def ping(self, interaction: disnake.ApplicationCommandInteraction) -> None:
        """
        Returns the bot's latency.

        Parameters
        ----------
        interaction : disnake.ApplicationCommandInteraction
            The interaction that invoked this command.
        """
        embed = await self.bot.embeds.ping_embed()
        await interaction.edit_original_response(embed=embed)

    @commands.slash_command(name="invite")
    async def invite(self, interaction: disnake.AppCmdInter) -> None:
        """
        Returns the bot's invite and related urls.
        """
        embed = (
            disnake.Embed(
                color=disnake.Color.red(),
                description=f"Thank you for using **{self.bot.user.name}**\n\n",
            )
            .set_author(name=f"Invite {self.bot.user.name}")
            .set_thumbnail(self.bot.user.avatar)
        )
        for head, value in {
            f"[Website]({self.bot.website_url})": "Please check out our website for detailed information on our bot.",
            f"[Support Server]({self.bot.server_url})": (
                "Feel free to check out our official server"
                " for updates on events and giveaways and more."
            ),
        }.items():
            assert embed.description
            embed.description += f"**{head}**\n{value}\n\n"
        await interaction.edit_original_message(
            embed=embed, view=invite_buttons_view(self.bot)
        )

    @commands.slash_command(name="botinfo")
    async def botinfo(self, interaction: disnake.AppCmdInter) -> None:
        """
        Information about the bot.
        """
        embed = disnake.Embed(
            color=disnake.Color.red(),
            description=f"""
                        {self.bot.embeds.ansi.from_string_to_ansi('Template discord bot. '
                        'Planned to contain moderation, utility, fun, and music commands. '
                        , Colors.MAGENTA, Styles.BOLD)}
                        """,
        ).set_author(name=self.bot.user.name, icon_url=self.bot.user.display_avatar)
        embed.add_field(name="Servers", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Users", value=len(self.bot.users), inline=True)
        await interaction.edit_original_response(embed=embed)
