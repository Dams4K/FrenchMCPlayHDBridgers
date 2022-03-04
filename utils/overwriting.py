from discord.commands.context import ApplicationContext
from utils.bot_data import GuildData

class BotApplicationContext(ApplicationContext):
    @property
    def guild_data(self):
        return GuildData(self.guild_id)