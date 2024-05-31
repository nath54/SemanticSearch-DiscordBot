"""_sumarry-
"""

import json
import os

from typing import cast

from discord_bot import DiscordBot


# Config file path, and the key of the discord api key in the config
CONFIG_FILE: str = "config.json"
CONFIG_DISCORD_KEY: str = "discord_api_key"


if __name__ == "__main__":

    # Test if config file exists
    if not os.path.exists(CONFIG_FILE):
        raise UserWarning(f"Config file `{CONFIG_FILE}` not found !")

    # Loading config
    config: dict[str, str | int] = {}

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)

    # Test if config file has the CONFIG_DISCORD_KEY key
    if CONFIG_DISCORD_KEY not in config:
        raise UserWarning(f"`{CONFIG_DISCORD_KEY}` not found in config !")

    # Launching the bot
    bot: DiscordBot = DiscordBot(config)

    bot.run(cast(str, config[CONFIG_DISCORD_KEY]))
