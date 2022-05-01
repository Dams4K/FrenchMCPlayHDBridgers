import discord
from discord import Option
from discord.ext import commands
from discord.commands import permissions, slash_command
from utils.references import References
from google.sheet import LeaderboardSheet
from utils.bot_data import Player
from discord.ext import bridge

class GlobalUserCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print(__name__, "on")


    @bridge.bridge_command(name="hello", guild_ids=References.BETA_GUILDS)
    async def hello_world(self, ctx):
        await ctx.respond("world")


    @bridge.bridge_command(name="testpb", guild_ids=References.BETA_GUILDS)
    async def test_pb_command(self, ctx,
        member: Option(discord.Member, "member", required=False) = None,
        normal: Option(float, "normal", required=False) = None,
        short: Option(float, "short", required=False) = None
    ):
        member = member if member else ctx.author
        w_data = ctx.guild_data.whitelist.get_data()
        p_uuid = list(w_data.keys())[list(w_data.values()).index(member.id)]
        player = Player(uuid=p_uuid)
        print(player.name)

def setup(bot):
    bot.add_cog(GlobalUserCommands(bot))