import discord
from discord.ext import commands
from discord.ext.commands.context import Context
from utils.lang.lang import Lang
from utils.references import References
from utils.checks import is_the_author
from utils.utils import aexec
from pathlib import Path

class OwnerCog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    async def cog_check(self, ctx: commands.Context):
        return is_the_author(ctx)

    @commands.command(name="stop")
    async def stop_bot(self, ctx):
        await self.bot.close()

    @commands.group(name="extensions", pass_context=True, invoke_without_command=True)
    async def extensions_manager(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            # await ctx.send("extensions")
            embed = discord.Embed(title="Cogs List")
            cogs = self.bot.get_cogs_file(References.COGS_FOLDER)
            description = ""
            extensions_used = [str(ext.__name__).replace(".", "/") + ".py" for ext in self.bot.extensions.values()]
            
            for cog in cogs:
                description += cog
                if cog in extensions_used:
                    description += " - <:checked:912038945599131660>"
                else:
                    description += " - <:unchecked:912038945834008607>"
                description += "\n"
            embed.description = description

            await ctx.send(embed=embed)
    
    @extensions_manager.command(name="load", pass_context=True)
    async def load_extension(self, ctx: commands.Context, extension_path: str):
        if extension_path in self.bot.get_cogs_file(References.COGS_FOLDER) and not extension_path in self.bot.extensions_path():
            self.bot.load_extension(extension_path.replace("/", ".")[:-3])
            await ctx.send("load")
        else:
            await ctx.send("error")
    
    @extensions_manager.command(name="unload", pass_context=True)
    async def unload_extension(self, ctx, extension_path):
        if extension_path in self.bot.get_cogs_file(References.COGS_FOLDER) and extension_path in self.bot.extensions_path():
            self.bot.unload_extension(extension_path.replace("/", ".")[:-3])
            await ctx.send("unload")
        else:
            await ctx.send("error")
    
    @extensions_manager.command("reload")
    async def reload_extension(self, ctx: commands.Context, extension_path: str):
        if extension_path in self.bot.get_cogs_file(References.COGS_FOLDER) and extension_path in self.bot.extensions_path():
            self.bot.reload_extension(extension_path.replace("/", ".")[:-3])
            await ctx.send("reload")
        else:
            await ctx.send("error")


    # This thing is cool but really risky for security
    # @commands.command(name="dsexec")
    # async def dsexec(self, ctx: Context, *, code):
    #     await aexec(code, ctx=ctx, bot=self.bot)
    #
    # This command can execute code and create new commands
    #
    # EXAMPLE:
    #
    # +dsexec
    # from discord.ext import commands
    # class TestCog(commands.Cog):
    #     def init(self, bot):
    #         self.bot = bot
    #     @commands.command(name="say")
    #     async def say(self, ctx, *, msg):
    #         await ctx.message.delete()
    #         await ctx.send(msg)
    # bot.add_cog(TestCog(bot))


def setup(bot: commands.Bot):
    bot.add_cog(OwnerCog(bot))
    pass