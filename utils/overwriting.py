from discord.commands.context import ApplicationContext
from discord.ext import commands
from utils.bot_data import GuildData

class BotApplicationContext(ApplicationContext):
    @property
    def guild_data(self):
        return GuildData(self.guild_id)

class BotContext(commands.Context):
    @property
    def guild_data(self):
        return GuildData(self.guild.id)
