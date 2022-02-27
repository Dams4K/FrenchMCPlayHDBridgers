from discord.ext import commands, tasks
from utils.bot_data import BaseData, KnownPlayers, Player

class BotLoops(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_names.start()


    @tasks.loop(hours=1)
    async def update_names(self):
        known_players = KnownPlayers()
        for player_data in known_players.data:
            player_data["name"] = Player(uuid=player_data["uuid"]).uuid_to_name()
        known_players.save_data()


def setup(bot):
    bot.add_cog(BotLoops(bot))