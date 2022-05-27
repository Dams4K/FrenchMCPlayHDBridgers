import discord
from discord.ext import commands
from utils.bot_logging import get_logging

class BotError(Exception):
    def __init__(self, message=""):
        self.message = message
        super().__init__(self.message)

class WhitelistError(BotError): pass

class PlayerExceptions(BotError): pass
class PlayerNotFound(PlayerExceptions): pass

def gen_error(msg: str) -> discord.Embed:
    return discord.Embed(title="Error", description=msg, color=0xff0000)

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