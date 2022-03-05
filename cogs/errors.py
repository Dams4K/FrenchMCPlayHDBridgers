import discord
from discord.ext import commands

class ErrorHandling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, exception):
        print(exception)
        embed=discord.Embed(title="Error", description=exception, color=0xff0000)
        await ctx.respond(embed=embed)
    

def setup(bot):
    bot.add_cog(ErrorHandling(bot))