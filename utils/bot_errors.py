import discord

class PlayerExceptions(Exception): pass

class PlayerNotFound(PlayerExceptions): pass

def gen_error(msg: str) -> discord.Embed:
    return discord.Embed(title="Error", description=msg, color=0xff0000)