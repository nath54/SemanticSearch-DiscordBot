from DiscordBot import DiscordBot
import json
import os


CONFIG_FILE: str = "config.json"
CONFIG_DISCORD_KEY: str = "discord_api_key"

if __name__ == "__main__":
    #
    if not os.path.exists(CONFIG_FILE):
        raise UserWarning(f"Config file `{CONFIG_FILE}` not found !")
    #
    f = open(CONFIG_FILE, "r")
    config: dict[str] = json.load(f)
    f.close()
    #
    if CONFIG_DISCORD_KEY not in config:
        raise UserWarning(f"`{CONFIG_DISCORD_KEY}` not found in config !")
    #
    bot: DiscordBot = DiscordBot(config)
    #
    # bot.run(config[CONFIG_DISCORD_KEY])
    #
    bot.run(config[CONFIG_DISCORD_KEY])
