from discord.commands.context import ApplicationContext
from discord.ext import bridge
from utils.bot_data import GuildData

class BotApplicationContext(bridge.context.BridgeApplicationContext):
    @property
    def guild_data(self):
        return GuildData(self.guild_id)

class BotContext(bridge.context.BridgeExtContext):
    @property
    def guild_data(self):
        return GuildData(self.guild.id)
