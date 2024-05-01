from DiscordBot import DiscordBot
import json
import os

if __name__ == "__main__":
    #
    if not os.path.exists("config.json"):
        raise UserWarning("No config files found !")
    #
    f = open("config.json", "r")
    config: dict[str] = json.load(f)
    f.close()
    #
    if "discord_api_key" not in config:
        raise UserWarning("No discord api key in config !")
    #
    bot: DiscordBot = DiscordBot(config)
    bot.run(config["discord_api_key"])
