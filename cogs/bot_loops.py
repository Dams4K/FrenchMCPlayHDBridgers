from discord.ext import commands, tasks

class BotLoops(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    


def setup(bot):
    bot.add_cog(BotLoops(bot))