from discord import slash_command
from discord.ext import commands
from utils.references import References

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @slash_command(
        name="test", description="Add player to the whitelist",
        guild_ids=References.BETA_GUILDS,
        options=[

        ])
    async def _test(self, ctx: SlashContext):
        await ctx.send("work fine")


def setup(bot):
    bot.add_cog(AdminCommands(bot))