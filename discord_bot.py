"""_summary_
"""

from typing import cast, Callable

import shlex
from aiostream import stream
import discord
from discord.ext import commands
from distance_calculator import DistanceCalculator


from profiling import Profile


class DiscordBot(commands.Bot):
    """_summary_

    Args:
        commands (_type_): _description_

    Raises:
        UserWarning: _description_

    Returns:
        _type_: _description_
    """


    #
    def __init__(self, config: dict[str, str | int]) -> None:
        #
        self.test_config(config)
        #
        self.config: dict[str, str | int] = config
        # Optional settings
        if not "profiling" in self.config:
            self.config["profiling"] = 0
        #
        intents = discord.Intents(messages=True, guilds=True)
        intents.message_content = True
        #
        self.command_prefix: str = cast(str, self.config["discord_command_prefix"])
        super().__init__(command_prefix=self.command_prefix,
                         intents=intents)
        #
        self.cmd_fcts: dict[str, Callable] = {
            "help": self.cmd_help,
            "ping": self.cmd_ping,
            "search": self.cmd_search,
            "search_simple": self.cmd_search_simple,
            "search_only_embed": self.cmd_search_only_embed
        }
        #
        self.distance_calc: DistanceCalculator = DistanceCalculator(config)


    #
    def test_config(self, config: dict[str, str | int]) -> None:
        """_summary_

        Args:
            config (dict[str, str  |  int]): _description_

        Raises:
            UserWarning: _description_
        """

        #
        c: str
        for c in ["discord_api_key", "discord_command_prefix", "model_name"]:
            if c not in config:
                raise UserWarning(f"`{c}` not found in config !")


    #
    async def on_ready(self) -> None:
        """_summary_
        """
        if self.user is not None:
            user: discord.ClientUser = cast(discord.ClientUser, self.user)
            print(f'Logged in as {user} (ID: {user.id})')


    #
    async def on_message(self, message: discord.Message) -> None:
        """_summary_

        Args:
            message (discord.Message): _description_

        Returns:
            _type_: _description_
        """

        if message.author == self.user:
            return  # Ignore messages sent by ourselves

        msg: str = message.content.lower()

        if not msg.startswith(self.command_prefix):
            return  # Ignore messages that doesn't start by command prefix

        cmd: str = msg[1:]  # Remove the command prefix here
        lcmd: list[str] = shlex.split(cmd)

        # Command Logic 
        if lcmd[0] in self.cmd_fcts:
            await self.cmd_fcts[lcmd[0]](lcmd, message)


    #
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

        if message.guild is None:
            return []

        guild: discord.Guild = cast(discord.Guild, message.guild)
        author: discord.Member = cast(discord.Member, message.author)
        # Iterate only through text channels
        channel: discord.TextChannel
        for channel in guild.text_channels:
            if channel.permissions_for(author).read_messages:
                channels.append(channel)
        #
        return channels


    #
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


    #
    async def cmd_ping(self, _: list[str],
                       message: discord.Message) -> None:
        """_summary_

        Args:
            _ (list[str]): _description_
            message (discord.Message): _description_
        """

        await message.reply("pong")


    #
    async def cmd_help(self, _: list[str],
                       message: discord.Message) -> None:
        """_summary_

        Args:
            _ (list[str]): _description_
            message (discord.Message): _description_
        """

        #
        msg_help: str = "This is a bot for semantic search.\n" \
                        "List of commands :"
        #
        for c in self.cmd_fcts:
            msg_help += f"\n    - {c}"
        #
        await message.reply(msg_help)


    #
    async def update_search(self,
                            taille_buffer: int,
                            buffer_bis: list[discord.Message],
                            min_msg_scores: list[tuple[discord.Message, float]],
                            dists: list[float],
                            message: discord.Message,
                            msg_reply: discord.Message | None
                           ) -> tuple[list[tuple[discord.Message, float]], discord.Message | None]:
        """_summary_

        Args:
            taille_buffer (int): _description_
            buffer_bis (list[discord.Message]): _description_
            min_msg_scores (list[tuple[discord.Message, float]]): _description_
            dists (list[float]): _description_
            message (discord.Message): _description_
            msg_reply (discord.Message | None): _description_

        Returns:
            tuple[list[tuple[discord.Message, float]], discord.Message | None]: _description_
        """

        # Looping through the buffer
        for i in range(taille_buffer):

            # 
            d: float = dists[i]
            msg_act: discord.Message = buffer_bis[i]

            #
            if len(min_msg_scores) < 3:
                #
                min_msg_scores.append(
                    (msg_act, d)
                )
            else:
                #
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
                    #
                    txt_reply = "Searching...\nCurrent Result:"
                    j: int = 1
                    for t in min_msg_scores:
                        txt_reply += f"\n {j}) {t[0].jump_url}"\
                                     f"(distance: {t[1]})"
                        j += 1
                    #
                    await msg_reply.edit(content=txt_reply)
        #
        return min_msg_scores, msg_reply


    #
    async def search(self,
                     lcmd: list[str],
                     message: discord.Message,
                     fct_calc_dist: Callable
                    )  -> None:
        """_summary_

        Args:
            lcmd (list[str]): _description_
            message (discord.Message): _description_
            fct_calc_dist (callable): _description_
        """

        # Profiling
        if self.config["profiling"] == 1:
            p1: Profile = Profile("DiscordBot.py; Parsing search args")

        # Parsing Option
        option_here: bool = False
        user_search: str = ""

        # Looking at all the command arguments
        i: int
        for i in range(1, len(lcmd)):

            # l is the current line argument
            l: str = lcmd[i]

            # Checkins special options
            if l.startswith("--"):
                # Option --here: check only messages on this current discord channel
                if l == "--here":
                    option_here = True
            #
            elif user_search == "":
                user_search = l

        # Profiling
        if self.config["profiling"] == 1:
            p1.finished()

        # If empty search, do nothing
        if user_search == "":
            return

        # Min msg scores will contain the list of the temporary best messages seen so far
        min_msg_scores: list[tuple[discord.Message, float]] = []

        # current discord channel and current message
        channel: discord.TextChannel
        msg: discord.Message

        # List of all the accessible channels by the user that made the research
        all_accessibles_channels: list[discord.TextChannel] = []

        # Profiling
        if self.config["profiling"] == 1:
            p2: Profile = Profile("DiscordBot.py; Get all accessible channels")

        # Get the accessible channels
        if option_here:
            all_accessibles_channels = [cast(discord.TextChannel, message.channel)]
        else:
            all_accessibles_channels = \
                await self.get_accessible_channels_for_user(message)

        # Profiling
        if self.config["profiling"] == 1:
            p2.finished()

        # Profiling
        if self.config["profiling"] == 1:
            p3: Profile = Profile("DiscordBot.py; Total search")

        # msg_reply will contain the object of the discord replied message
        msg_reply: discord.Message | None = None

        # Counter of all the messages we have processed here during the search
        total_msgs_processed: int = 0

        # Profiling
        if self.config["profiling"] == 1:
            p5: Profile = Profile("DiscordBot.py; Embed Messages")

        # Looping through all the accessible channels
        for channel in all_accessibles_channels:

            # Profiling
            if self.config["profiling"] == 1:
                p4: Profile = Profile( "DiscordBot.py;"
                                       "Get all accessible messages from channel : "
                                      f"<<{channel.name}>>")

            # Getting all the messages of this channel
            all_messages: list[discord.Message] = \
                await self.get_all_messages(channel)

            # Profiling
            if self.config["profiling"] == 1:
                p4.finished()

            # Initialising buffer
            buffer_bis: list[discord.Message] = []
            buffer: list[str] = []
            taille_buffer: int = 0
            taille_max_buffer: int = 16

            # Looping through all the messages of this channel
            for msg in all_messages:

                # Ignoring command messages or from this discord bot
                if msg.content.startswith(self.command_prefix):
                    continue
                if msg.author == "Semantic Search":
                    continue

                # Adding the current message to the buffer
                buffer_bis.append(msg)
                buffer.append(msg.content)
                taille_buffer += 1

                # If the buffer is full, processing the buffer
                if taille_buffer >= taille_max_buffer:

                    # Calculate the distances of theses messages from the search input
                    dists: list[float] = fct_calc_dist(user_search, buffer)

                    # Profiling
                    if self.config["profiling"] == 1:
                        p5.intermediate_update(f"Buffer size : {taille_buffer}")

                    # Update the search results
                    min_msg_scores, msg_reply = await self.update_search(
                        taille_buffer,
                        buffer_bis,
                        min_msg_scores,
                        dists,
                        message,
                        msg_reply
                    )
                    total_msgs_processed += taille_buffer

                    # Reset the buffer
                    taille_buffer = 0
                    buffer = []
                    buffer_bis = []

        # If there are messages left in the buffer
        if taille_buffer > 0:

            # Calculate the distances of theses messages from the search input
            distances: list[float] = fct_calc_dist(user_search, buffer)

            # Update the search results
            min_msg_scores, msg_reply = await self.update_search(
                taille_buffer,
                buffer_bis,
                min_msg_scores,
                distances,
                message,
                msg_reply
            )
            total_msgs_processed += taille_buffer

        # Profiling
        if self.config["profiling"] == 1:
            p5.finished(f"Total msgs processed: {total_msgs_processed}")

        # Sorting the message results
        min_msg_scores.sort(key=lambda t: t[1])

        # Final Result Message Answer Text
        txt_reply = "Search Result:"
        j: int = 1
        for t in min_msg_scores:
            txt_reply += f"\n {j}) {t[0].jump_url} (distance: {t[1]})"
            j += 1

        # Profiling
        if self.config["profiling"] == 1:
            p3.finished()

        # Send / Update the final search results answer message
        if msg_reply is None:
            await message.reply(content=txt_reply)
        else:
            await msg_reply.edit(content=txt_reply)


    #
    async def cmd_search(self, lcmd: list[str],
                         message: discord.Message) -> None:
        """_summary_

        Args:
            lcmd (list[str]): _description_
            message (discord.Message): _description_
        """

        # Profiling
        if self.config["profiling"] == 1:
            p: Profile = Profile("DiscordBot.py; search.calculate_distance_both")

        # Calling the search with the good distance function
        await self.search(lcmd,
                          message,
                          self.distance_calc.calculate_distance_both)

        # Profiling
        if self.config["profiling"] == 1:
            p.finished()


    #
    async def cmd_search_simple(self, lcmd: list[str],
                                message: discord.Message) -> None:
        """_summary_

        Args:
            lcmd (list[str]): _description_
            message (discord.Message): _description_
        """

        # Profiling
        if self.config["profiling"] == 1:
            p: Profile = Profile("DiscordBot.py; search.calculate_distance_common_words")

        # Calling the search with the good distance function
        await self.search(lcmd,
                          message,
                          self.distance_calc.calculate_distance_common_words)

        # Profiling
        if self.config["profiling"] == 1:
            p.finished()


    #
    async def cmd_search_only_embed(self, lcmd: list[str],
                                    message: discord.Message) -> None:
        """_summary_

        Args:
            lcmd (list[str]): _description_
            message (discord.Message): _description_
        """

        # Profiling
        if self.config["profiling"] == 1:
            p: Profile = Profile("DiscordBot.py; search.calculate_distance_embed")

        # Calling the search with the good distance function
        await self.search(lcmd,
                          message,
                          self.distance_calc.calculate_distance_embed)

        # Profiling
        if self.config["profiling"] == 1:
            p.finished()
