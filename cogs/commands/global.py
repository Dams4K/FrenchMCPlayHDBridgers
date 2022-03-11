import discord
from discord import Option
from discord.ext import commands
from discord.commands import permissions, slash_command
from utils.references import References

class GlobalUserCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @slash_command(name="hello", guild_ids=References.BETA_GUILDS)
    async def set_new_pb_channel(self, ctx):
        await ctx.respond("world")


def setup(bot):
    bot.add_cog(GlobalUserCommands(bot))