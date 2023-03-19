# Setup

create a .env file with the following contents

```txt
TOKEN="DISCORD_BOT_TOKEN"
PGURL="LINK_TO_YOUR_POSTGRES_DATABASE"
```

---

# Installation

Make sure you have poetry installed if you do follow the following steps

```bash
$poetry init
$ poetry install
```

If not

```bash
$python -m venv venv
$venv\Scripts\activate
$pip install -r requirements.txt
```
for ubuntu and other distros

```
$source venv/bin/activate
```

All above assumes you have python 3.10 or higher installed on your system

---

# Running

After all dependencies are installed

```bash
$python __main__.py
```

# Add new commands

Inherit the `src.ext.BaseCog` class and add the `@commands.slash_command()` decorator to add commands.
All cogs are automatically loaded and added to the bot and help command.
All interactions are automatically deferred to prevent the interaction from timing out.


```python
import disnake
from disnake.ext import commands
from src.ext import BaseCog


class MyCog(BaseCog):

    @commands.slash_command()
    async def my_command(self, inter: disnake.ApplicationCommandInteraction) -> None:
        await inter.send("Hello World")

```

# Add new Views

There are premade paginators in src/core/views/paginators for free use which include file paginator, normal embed paginator and select menu paginator.
For custom views inherit the `src.core.views.BaseView` class and add respective components to your view.

## Benefits of using the BaseView class

- All views are automatically error handled
- Premade timeout and disable methods
- Custom interaction handling and checks


# Add new table to the database

Inherit the `src.database.tables._table.Table` class to create a new table.
All tables are automatically created when the bot is started and migrations are automatically applied.
Each table is automatically added to the `src.database.Database` class.
To add your own table to the database add it is recommended to use it with your own custom models which can be made in `src.database.models`.


# Notes

- It is recommended to have thorough knowledge of the following libraries before using this template
    - disnake
    - asyncpg
    - poetry
    - attrs
- The following concepts are also needed
    - OOP
    - SQL
    - Asyncio
    - Structural Programming

The bot also has a bunch of other features such as file logger and stream logger. Custom exceptional handler eval commands and a bunch of other handy tools to assist a developer.

# Help

If you need help with using this or working with the bot feel free to contact me on discord at `Asher#0738` or on github at `FallenDeity`.
