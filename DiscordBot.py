import discord
from discord.ext import commands
from EmbeddingCalculator import EmbeddingCalculator
import shlex

class DiscordBot(commands.Bot):
    def __init__(self, config: dict[str]) -> None:
        #
        self.test_config(config)
        #
        self.config: dict[str] = config
        #
        super().__init__(command_prefix=self.config["discord_command_prefix"])
        #
        self.cmd_fcts: dict = {
            "ping": self.cmd_ping
        }
        # Loading model
        self.embedding_calc = EmbeddingCalculator(
            model_name=config["model_name"],
            use_cuda=config["use_cuda"] if "use_cuda" in config else False
        )
        #

    def test_config(self, config: dict[str]) -> None:
        #
        for c in ["discord_api_key", "discord_command_prefix", "model_name"]:
            if c not in config:
                raise UserWarning(f"`{c}` not found in config !")
        #

    async def on_ready(self) -> None:
        print(f'Logged in as {self.user} (ID: {self.user.id})')


    async def on_message(self, message) -> None:
        if message.author == self.user:
            return  # Ignore messages sent by ourselves

        msg: str = message.content.lower()

        if not msg.startswith(self.config["discord_command_prefix"]):
            return  # Ignore messages that doesn't start by command prefix

        cmd: str = msg[1:]  # Remove the command prefix here
        lcmd: list[str] = shlex.split(cmd)

        # Command Logic 
        if lcmd[0] in self.cmd_fcts:
            self.cmd_fcts[lcmd[0]](lcmd, message)
        else:
            print(f"Error: Unknown Command {lcmd[0]}")

    async def cmd_ping(self, lcmd: list[str], message) -> None:
        message.channel.send("pong")

    async def cmd_search(self, lcmd: list[str], message) -> None:
        pass
        # TODO: get all the channels the user have access
        # TODO: Do a semantic search to find closest messages to the search
