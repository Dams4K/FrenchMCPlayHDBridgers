import discord
from discord.ext import commands
from utils.bot_logging import get_logging

class ErrorHandling(commands.Cog):
    logging_error = get_logging(__name__, "error")

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, exception):
        self.logging_error.error(exception)
        embed=discord.Embed(title="Error", description=exception, color=0xff0000)
        await ctx.respond(embed=embed)
    

def setup(bot):
    bot.add_cog(ErrorHandling(bot))