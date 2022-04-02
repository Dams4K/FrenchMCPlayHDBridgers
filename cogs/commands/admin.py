import discord
from discord import Option
from discord.ext import commands
from discord.commands import permissions, slash_command

from utils.references import References
from utils.overwriting import BotApplicationContext
from utils.lang.lang import Lang
from utils.checks import *

class GlobalAdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @slash_command(name="set_new_pb_channel", checks=[can_moderate])
    async def set_new_pb_channel(
        self, ctx: BotApplicationContext, 
        channel: Option(discord.TextChannel, "channel", required=True)
    ):
        ctx.guild_data.set_pb_channel(channel.id)
        await ctx.respond(Lang.get_text("NEW_PB_CHANNEL_CHANGE", "fr", channel=channel))


def setup(bot):
    bot.add_cog(GlobalAdminCommands(bot))