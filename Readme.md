# Semantic Search

## Short description

The goal of this project is to build a small Discord Bot that search messages in discord channels. It does semantic search along simple word search. It is compatible with multiple LLM Semantic Models, like Bert or e5 for instance.


## How to use

### Dependencies

You will need to have the following python libraries to be able to launch this program: 
    * discord
    * numpy
    * transformers
    * torch

So, if you are missing ones, you can install them with "your_python_executable -m pip install lib_1, lib_2, ..., lib_n"


### Create a discord bot

You will need to create a discord bot on the discord website, you can follow theses instructions: [](https://discord.com/developers/docs/quick-start/getting-started).


### Configuration file

You will need to create a configuration file to launch this program. The configuration have 4 parametrable options:
    * `discord_api_key`: your discord api key to connect the bot to discord, you can find it on the discord website.
    * `discord_command_prefix`: This is the prefix you want your bot listen to detect a command search.
    * `model_name` This is the model you want to use for calculate messages embedding for semantic search.
    * `use_cuda` Set to 1 if you want to use your nvidia gpu to calculate embeddings, if you don't have nvidia gpu or/and you want to use your cpu instead, set this option to 0.

The configuration use the JSON format. The configuration file path from the project root folder is `./config.txt`

Here is an example of a configuration file:

```json
{
    "discord_api_key": "PUT HERE DISCORD API KEY",
    "discord_command_prefix": "!",
    "model_name": "intfloat/multilingual-e5-large",
    "use_cuda": 1
}
```

### How to use the bot in discord

For the examples, we suppose that the configuration `discord_command_prefix` is set to "!"

To use the bot to search a sentence, you must be in a channel accessible by the bot, and write one of the following commands:
    * `!search "SEARCH_INPUT"`: search with a mix of semantic search + simple word search
    * `!search_simple "SEARCH_INPUT"`: search with a simple word search
    * `!search_only_embed "SEARCH_INPUT"`: search with semantic search
    * `!ping`: test if the bot is working
    * `!help`: display an help message


All the commands accepts the `--here` option, which limits the search to the discord channel where the command is typed.

