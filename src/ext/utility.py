import typing

import disnake
from disnake.ext import commands

from src.utils.help import Help

from . import BaseCog


class Utility(BaseCog):
    """Utility commands for the bot displaying information about the bot."""

    @property
    def command_names(self) -> list[str]:
        all_commands: list[str] = []
        for command in self.bot.slash_commands:
            if typing.cast(BaseCog, command.cog).hidden:
                continue
            for subcommand in command.children.values():
                all_commands.append(subcommand.qualified_name)
            all_commands.append(command.qualified_name)
        return all_commands

    @commands.slash_command(name="help", description="Get help about a command or category.")
    async def help_command(self, inter: disnake.ApplicationCommandInteraction, argument: str | None = None) -> None:
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
        _list = [cog for cog in bot.cogs if arg.lower() in cog.lower() and not typing.cast(BaseCog, cog).hidden]
        _list.extend(self.command_names)
        return _list[:25]

    @commands.slash_command(name="clear", description="Clear a certain amount of messages.")
    async def clear_command(
        self,
        inter: disnake.ApplicationCommandInteraction,
        amount: commands.Range[int, 1, 100],
    ) -> None:
        """Clear a certain amount of messages.

        Parameters
        ----------
        inter : disnake.ApplicationCommandInteraction
            The interaction that invoked this command.
        amount : int
            The amount of messages to clear.
        """
        channel: disnake.TextChannel = typing.cast(disnake.TextChannel, inter.channel)
        await channel.purge(limit=amount + 1)
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
