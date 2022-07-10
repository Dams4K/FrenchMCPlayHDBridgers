import json
import discord
import os
from discord.ext import bridge
from utils.references import References
from utils.overwriting import *
from utils.bot_logging import get_logging

class LeaderboardBot(bridge.Bot):
    def __init__(self):
        super().__init__(self.get_prefix, case_insensitive=True, help_command=None, intents=discord.Intents.all(), debug_guilds=[912435770290229348, 892459726212837427])
        self.logging_info = get_logging(__name__, "info")

    
    async def on_ready(self):
        os.system("clear||cls")
        print(self.user, "is now ready")
        print("version:", References.VERSION)
        self.logging_info.info("Bot started")
        

    async def get_application_context(self, interaction, cls = BotApplicationContext):
        return await super().get_application_context(interaction, cls=cls)


    async def get_context(self, message, *, cls = BotContext):
        return await super().get_context(message, cls=cls)



    def load_cogs(self, path: str):
        # await self.wait_until_ready()
        for cog_file in self.get_cogs_file(path):
            self.load_extension(cog_file.replace("/", ".")[:-3])


    def get_cogs_file(self, path: str) -> list:
        cogs_file = []

        for filename in os.listdir(path):
            if os.path.isfile(path + "/" + filename):
                if filename.endswith(".py"):
                    cogs_file.append(f"{path}/{filename}")
            
            elif os.path.isdir(path + "/" + filename):
                cogs_file += self.get_cogs_file(path + "/" + filename)

        return cogs_file
    
    def extensions_path(self):
        return [str(ext.__name__).replace(".", "/") + ".py" for ext in self.extensions.values()]

    async def get_prefix(bot, message):
        return References.BOT_PREFIX
