from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from utils.references import References

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @cog_ext.cog_slash(
        name="test", description="Add player to the whitelist",
        guild_ids=References.BETA_GUILDS,
        options=[

        ])
    @commands.has_guild_permissions(administrator=True)
    async def _test(self, ctx: SlashContext):
        await ctx.send("work fine")


def setup(bot):
    bot.add_cog(AdminCommands(bot))