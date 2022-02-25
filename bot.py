import json
import discord
import os
from discord.ext import commands
from utils.references import References

class LeaderboardBot(commands.Bot):
    def __init__(self):
        super().__init__(self.get_prefix, case_insensitive=True, help_command=None, intents=discord.Intents.all())
    
    async def on_ready(self):
        os.system("clear||cls")
        print(self.user, "is now ready")
        print("version:", References.VERSION)

    def load_cogs(self, path: str):
        for filename in os.listdir(path):
            if os.path.isfile(path + "/" + filename):
                if filename.endswith(".py"):
                    cog_path = path.replace("/", ".")
                    self.load_extension(f"{cog_path}.{filename[:-3]}")
            elif os.path.isdir(path + "/" + filename):
                self.load_cogs(path + "/" + filename)


    async def get_prefix(bot, message):
        return References.BOT_PREFIX
