import discord
from discord.ext import commands
from DistanceCalculator import DistanceCalculator
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
        #
        self.distance_calc: DistanceCalculator = DistanceCalculator(
            model_name=config["model_name"],
            use_cuda=config["use_cuda"] if "use_cuda" in config else False
        )
        #

    def test_config(self, config: dict[str]) -> None:
        #
        c: str
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

    async def get_accessible_channels(self,
                                      message: discord.Message
                                        ) -> list[discord.ChannelType]:
        """
        Gets all channels the message author has access to
        (read messages permission)

        Args:
            message (discord.Message): The message object

        Returns:
            list: A list of discord.TextChannel objects
                    the author has access to
        """
        channels: list[discord.ChannelType] = []
        guild: discord.Guild = message.guild
        # Iterate only through text channels
        channel: discord.ChannelType
        for channel in guild.text_channels:
            if channel.permissions_for(message.author).read_messages:
                channels.append(channel)
        #
        return channels
    
    async def get_all_messages(self,
                               channel: discord.ChannelType
                                ) -> list[discord.Message]:
        """
        Gets all messages from a channel with pagination

        Args:
            channel (discord.TextChannel): The channel object to get
                                                messages from

        Returns:
            list: A list of discord.Message objects from the channel
        """
        messages: list[discord.Message] = []
        last_message_id: int | None = None
        while True:
            fetched_messages = await channel.history(
                                        limit=100,
                                        before=last_message_id).flatten()
            if not fetched_messages:
                break
            messages.extend(fetched_messages)
            last_message_id = messages[-1].id  # Get the ID of the last message
        return messages

    async def cmd_ping(self, lcmd: list[str],
                       message: discord.Message) -> None:
        message.channel.send("pong")

    async def cmd_search(self, lcmd: list[str],
                         message: discord.Message) -> None:
        #
        min_msg_scores: list[tuple[discord.Message, float]] = []
        #
        channel: discord.ChannelType
        for channel in self.get_accessible_channels(message):
            pass

