import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext

class ErrorHandling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_command_error(self, ctx, exception):
        await self.on_error(ctx, exception)
    
    @commands.Cog.listener()
    async def on_slash_command_error(self, ctx, exception):
        await self.on_error(ctx, exception)
    
    async def on_error(self, ctx, exception):
        embed=discord.Embed(title="Error", description=exception, color=0xff0000)
        await ctx.send(embed=embed)

def setup(bot):
    # bot.add_cog(ErrorHandling(bot))
    pass