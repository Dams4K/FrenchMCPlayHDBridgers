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


    @slash_command(name="set_new_pb_channel", checks=[can_moderate], guild_ids=References.BETA_GUILDS)
    async def set_new_pb_channel(
        self, ctx: BotApplicationContext, 
        channel: Option(discord.TextChannel, "channel", required=True)
    ):
        ctx.guild_data.set_pb_channel(channel.id)
        await ctx.respond(Lang.get_text("NEW_PB_CHANNEL_CHANGE", "fr", channel=channel))


    @slash_command(name="send_pb", checks=[can_moderate], guild_ids=References.BETA_GUILDS)
    async def send_pb(
        self, ctx,
        player_name: Option(str, "player_name", description="just the name", required=True),
        normal_time: Option(float, "normal_time", description="in seconds", required=False),
        short_time: Option(float, "short_time", description="in seconds", required=False)
    ):
        channel_id = ctx.guild_data.get_pb_channel()
        channel = discord.utils.get(ctx.guild.text_channels, id=channel_id)
        if normal_time > 0: await channel.send(Lang.get_text("SAME_PB", "fr", member_mention=player_name, mode="normal", score=normal_time))
        if short_time > 0: await channel.send(Lang.get_text("SAME_PB", "fr", member_mention=player_name, mode="short", score=short_time))


def setup(bot):
    bot.add_cog(GlobalAdminCommands(bot))