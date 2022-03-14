import json
import discord
import os
from discord.ext import commands
from utils.references import References
from utils.overwriting import *

class LeaderboardBot(commands.Bot):
    def __init__(self):
        super().__init__(self.get_prefix, case_insensitive=True, help_command=None, intents=discord.Intents.all())
    
    async def on_ready(self):
        os.system("clear||cls")
        print(self.user, "is now ready")
        print("version:", References.VERSION)
        await self.load_cogs(References.COGS_FOLDER)
    

    async def on_application_command(self, ctx: BotApplicationContext):
        print(ctx.command.qualified_name)


    async def get_application_context(self, interaction, cls = None):
        if cls is None:
            cls = BotApplicationContext
            
        return cls(self, interaction)


    async def load_cogs(self, path: str):
        await self.wait_until_ready()
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
