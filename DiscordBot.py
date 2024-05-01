import discord
from discord.ext import commands
from DistanceCalculator import DistanceCalculator
import shlex
from aiostream import stream

def get_dist_inferior(lst_msgs_with_dists: list[tuple[discord.Message, float]],
                      distance: float) -> int:
    #
    i = 0
    for t in lst_msgs_with_dists:
        if t[1] > distance:
            return i
        i+=1
    #
    return -1

class DiscordBot(commands.Bot):
    def __init__(self, config: dict[str]) -> None:
        #
        self.test_config(config)
        #
        self.config: dict[str] = config
        #
        intents = discord.Intents(messages=True, guilds=True)
        intents.message_content = True
        #
        super().__init__(command_prefix=self.config["discord_command_prefix"],
                         intents=intents)
        #
        self.cmd_fcts: dict = {
            "ping": self.cmd_ping,
            "search": self.cmd_search
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


    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.user:
            return  # Ignore messages sent by ourselves

        msg: str = message.content.lower()

        print(f"Received something "
              f"(content: {message.content}, "
              f"author: {message.author}, "
              f"channel: {message.channel}, "
              f"guild: {message.guild}")

        if not msg.startswith(self.config["discord_command_prefix"]):
            return  # Ignore messages that doesn't start by command prefix

        cmd: str = msg[1:]  # Remove the command prefix here
        lcmd: list[str] = shlex.split(cmd)

        # Command Logic 
        if lcmd[0] in self.cmd_fcts:
            await self.cmd_fcts[lcmd[0]](lcmd, message)
        else:
            print(f"Error: Unknown Command {lcmd[0]}")

    async def get_accessible_channels_for_user(self,
                                      message: discord.Message
                                        ) -> list[discord.TextChannel]:
        """
        Gets all channels the message author has access to
        (read messages permission)

        Args:
            message (discord.Message): The message object

        Returns:
            list: A list of discord.TextChannel objects
                    the author has access to
        """
        channels: list[discord.TextChannel] = []
        guild: discord.Guild = message.guild
        # Iterate only through text channels
        channel: discord.TextChannel
        for channel in guild.text_channels:
            if channel.permissions_for(message.author).read_messages:
                channels.append(channel)
        #
        return channels
    
    async def get_all_messages(self,
                               channel: discord.TextChannel
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
        last_message: discord.Message | None = None
        while True:
            fetched_messages: list[discord.Message] = await stream.list(
                                                        channel.history(
                                                        limit=100,
                                                        before=last_message)
                                                      )
            if not fetched_messages:
                break
            messages.extend(fetched_messages)
            last_message = messages[-1]  # Get the ID of the last message
        #
        return messages

    async def cmd_ping(self, lcmd: list[str],
                       message: discord.Message) -> None:
        await message.channel.send("pong")

    async def cmd_search(self, lcmd: list[str],
                         message: discord.Message) -> None:
        #
        option_here: bool = False
        user_search: str = ""
        #
        i: int
        for i in range(1, len(lcmd)):
            #
            l: str = lcmd[i]
            #
            if l.startswith("--"):
                if l == "--here":
                    option_here = True
                else:
                    # Unkown option, do nothing
                    pass
            #
            elif user_search == "":
                user_search = l
        #
        if user_search == "":
            
            return
        #
        min_msg_scores: list[tuple[discord.Message, float]] = []
        #
        channel: discord.TextChannel
        msg: discord.Message
        #
        all_accessibles_channels: list[discord.TextChannel] = []
        #
        if option_here:
            all_accessibles_channels = [message.channel]
        else:
            all_accessibles_channels = \
                await self.get_accessible_channels_for_user(message)
        #
        for channel in all_accessibles_channels:
            #
            all_messages: list[discord.Message] = \
                await self.get_all_messages(channel)
            #
            for msg in all_messages:
                d: float = self.distance_calc.calculate_distance(user_search,
                                                                 msg.content)
                if len(min_msg_scores) < 3:
                    min_msg_scores.append(
                        (msg, d)
                    )
                else:
                    idx: int = get_dist_inferior(min_msg_scores, d)
                    if idx != -1:
                        min_msg_scores[idx] = (msg, d)
        #
        min_msg_scores.sort(key=lambda t: t[1])
        #
        txt_reply = "Search Result:"
        i: int = 1
        for t in min_msg_scores:
            txt_reply += f"\n {i}) {t[0].jump_url} (distance: {t[1]})"
            i += 1
        #
        await message.reply(txt_reply)

