import discord
from discord.ext import commands
from DistanceCalculator import DistanceCalculator
import shlex
from aiostream import stream


from profiling import Profile


class DiscordBot(commands.Bot):
    def __init__(self, config: dict[str]) -> None:
        #
        self.test_config(config)
        #
        self.config: dict[str] = config
        # Optional settings
        if not "profiling" in self.config:
            self.config["profiling"] = 0
        #
        intents = discord.Intents(messages=True, guilds=True)
        intents.message_content = True
        #
        super().__init__(command_prefix=self.config["discord_command_prefix"],
                         intents=intents)
        #
        self.cmd_fcts: dict = {
            "help": self.cmd_help,
            "ping": self.cmd_ping,
            "search": self.cmd_search,
            "search_simple": self.cmd_search_simple,
            "search_only_embed": self.cmd_search_only_embed
        }
        #
        self.distance_calc: DistanceCalculator = DistanceCalculator(
            config=self.config
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

        # print(f"Received something "
        #       f"(content: {message.content}, "
        #       f"author: {message.author}, "
        #       f"channel: {message.channel}, "
        #       f"guild: {message.guild}")

        if not msg.startswith(self.config["discord_command_prefix"]):
            return  # Ignore messages that doesn't start by command prefix

        cmd: str = msg[1:]  # Remove the command prefix here
        lcmd: list[str] = shlex.split(cmd)

        # Command Logic 
        if lcmd[0] in self.cmd_fcts:
            await self.cmd_fcts[lcmd[0]](lcmd, message)
        else:
            pass
            # print(f"Error: Unknown Command {lcmd[0]}")

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
        await message.reply("pong")

    async def cmd_help(self, lcmd: list[str],
                       message: discord.Message) -> None:
        #
        msg_help: str = "This is a bot for semantic search.\n" \
                        "List of commands :"
        #
        for c in self.cmd_fcts:
            msg_help += f"\n    - {c}"
        #
        await message.reply(msg_help)

    async def update_search(self,
                            taille_buffer: int,
                            buffer_bis: list[discord.Message],
                            min_msg_scores: list[tuple[discord.Message, float]],
                            dists: list[float],
                            message: discord.Message,
                            msg_reply: discord.Message | None
        ) -> tuple[list[tuple[discord.Message, float]], discord.Message | None]:
        #
        for i in range(taille_buffer):
            #
            d: float = dists[i]
            msg_act: discord.Message = buffer_bis[i]
            #
            if len(min_msg_scores) < 3:
                min_msg_scores.append(
                    (msg_act, d)
                )
            else:
                min_msg_scores.sort(key=lambda t: t[1])
                #
                update_msg: bool = False
                #
                if min_msg_scores[-1][1] > d:
                    min_msg_scores[-1] = (msg_act, d)
                    update_msg = True
                #
                if msg_reply is None:
                    update_msg = True
                    msg_reply = await message.reply("Searching...")
                #
                if update_msg:
                    last_update = 0
                    #
                    txt_reply = "Searching...\nCurrent Result:"
                    i: int = 1
                    for t in min_msg_scores:
                        txt_reply += f"\n {i}) {t[0].jump_url}"\
                                    f"(distance: {t[1]})"
                        i += 1
                    #
                    await msg_reply.edit(content=txt_reply)
        #
        return min_msg_scores, msg_reply


    async def search(self,
                     lcmd: list[str],
                     message: discord.Message,
                     fct_calc_dist: callable
                    )  -> None:
        #
        if self.config["profiling"] == 1:
            p1: Profile = Profile("DiscordBot.py; Parsing search args")
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
        if self.config["profiling"] == 1:
            p1.finished()
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
        if self.config["profiling"] == 1:
            p2: Profile = Profile("DiscordBot.py; Get all accessible channels")
        #
        if option_here:
            all_accessibles_channels = [message.channel]
        else:
            all_accessibles_channels = \
                await self.get_accessible_channels_for_user(message)
        #
        if self.config["profiling"] == 1:
            p2.finished()
        #
        if self.config["profiling"] == 1:
            p3: Profile = Profile("DiscordBot.py; Total search")
        #
        msg_reply: discord.Message | None = None
        total_msgs_processed: int = 0
        #
        if self.config["profiling"] == 1:
            p5: Profile = Profile("DiscordBot.py; Embed Messages")
        #
        for channel in all_accessibles_channels:
            #
            if self.config["profiling"] == 1:
                p4: Profile = Profile(f"DiscordBot.py; Get all accessible messages from channel : <<{channel.name}>>")
            #
            all_messages: list[discord.Message] = \
                await self.get_all_messages(channel)
            #
            if self.config["profiling"] == 1:
                p4.finished()
            #
            buffer_bis: list[discord.Message] = []
            buffer: list[str] = []
            taille_buffer: int = 0
            taille_max_buffer: int = 16
            #
            for msg in all_messages:
                if msg.content.startswith(
                    self.config["discord_command_prefix"]):
                    continue
                if msg.author == "Semantic Search":
                    continue
                #
                buffer_bis.append(msg)
                buffer.append(msg.content)
                taille_buffer += 1
                if taille_buffer >= taille_max_buffer:
                    dists: list[float] = fct_calc_dist(user_search, buffer)
                    #
                    if self.config["profiling"] == 1:
                        p5.intermediate_update([f"Buffer size : {taille_buffer}"])
                    #
                    min_msg_scores, msg_reply = await self.update_search(
                        taille_buffer,
                        buffer_bis,
                        min_msg_scores,
                        dists,
                        message,
                        msg_reply
                    )
                    total_msgs_processed += taille_buffer
                    taille_buffer = 0
                    buffer = []
                    buffer_bis = []
        #
        if taille_buffer > 0:
            #
            dists: list[float] = fct_calc_dist(user_search, buffer)
            #
            min_msg_scores, msg_reply = await self.update_search(
                taille_buffer,
                buffer_bis,
                min_msg_scores,
                dists,
                message,
                msg_reply
            )
            total_msgs_processed += taille_buffer
            taille_buffer = 0
            buffer = []
            buffer_bis = []
        #
        if self.config["profiling"] == 1:
            p5.finished([f"Total msgs processed: {total_msgs_processed}"])
        #
        min_msg_scores.sort(key=lambda t: t[1])
        #
        txt_reply = "Search Result:"
        i: int = 1
        for t in min_msg_scores:
            txt_reply += f"\n {i}) {t[0].jump_url} (distance: {t[1]})"
            i += 1
        #
        if self.config["profiling"] == 1:
            p3.finished()
        #
        if msg_reply is None:
            await message.reply(content=txt_reply)
        else:
            await msg_reply.edit(content=txt_reply)
        
        

    async def cmd_search(self, lcmd: list[str],
                         message: discord.Message) -> None:
        #
        if self.config["profiling"] == 1:
            p: Profile = Profile("DiscordBot.py; search.calculate_distance_both")
        #
        await self.search(lcmd,
                          message,
                          self.distance_calc.calculate_distance_both)
        #
        if self.config["profiling"] == 1:
            p.finished()
        
    
    async def cmd_search_simple(self, lcmd: list[str],
                         message: discord.Message) -> None:
        #
        if self.config["profiling"] == 1:
            p: Profile = Profile("DiscordBot.py; search.calculate_distance_common_words")
        #
        await self.search(lcmd,
                          message,
                          self.distance_calc.calculate_distance_common_words)
        #
        if self.config["profiling"] == 1:
            p.finished()
    
    async def cmd_search_only_embed(self, lcmd: list[str],
                         message: discord.Message) -> None:
        #
        if self.config["profiling"] == 1:
            p: Profile = Profile("DiscordBot.py; search.calculate_distance_embed")
        #
        await self.search(lcmd,
                          message,
                          self.distance_calc.calculate_distance_embed)
        #
        if self.config["profiling"] == 1:
            p.finished()
