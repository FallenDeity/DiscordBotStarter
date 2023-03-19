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
$poetry install
```

If not

```bash
$python -m venv venv
$venv\Scripts\activate
$pip install disnake python-dotenv humanfriendly asyncpg durations-nlp chat-exporter
```
for ubuntu and other distros

```
$source venv\bin\activate
```

All above assumes you have python 3.10 or higher installed on your system

---

# Running

After all dependencies are installed

```bash
$python __main__.py
```
