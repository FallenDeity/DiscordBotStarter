import typing

import disnake

if typing.TYPE_CHECKING:
    from src import TemplateBot


def invite_buttons_view(bot: "TemplateBot") -> disnake.ui.View:
    view = disnake.ui.View()
    buttons_map: dict[str, tuple[str, disnake.Emoji | str | None]] = {
        "Invite Bot": (bot.invite_url, "ℹ️"),
        "Website": (bot.website_url, "🌐"),
        "Support Server": (bot.server_url, "👥"),
    }
    for label, data in buttons_map.items():
        view.add_item(
            disnake.ui.Button(
                style=disnake.ButtonStyle.url, label=label, url=data[0], emoji=data[1]
            )
        )
    return view
