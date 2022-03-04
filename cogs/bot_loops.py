import asyncio, time, discord
from discord.ext import commands, tasks
from utils.bot_data import BaseData, KnownPlayers, Player, GuildData
from google import sheet

class BotLoops(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.update_players_data.start()


    @tasks.loop(seconds=600)
    async def update_players_data(self):
        KnownPlayers.load_data()
        current_data = KnownPlayers.get_data()

        guild_data = GuildData(912435770290229348) #TODO: transformer ça pour que ça marche sur tout les servs

        for i_player_data in current_data:
            player_data = KnownPlayers.data[i_player_data]
            player = Player(uuid=player_data["uuid"])
            last_update = player_data["last_update"]

            print(player.name)

            if round(time.time()) - last_update > self.update_players_data._sleep:
                print("update")
                player_data["name"] = player.uuid_to_name()
                player_data["last_update"] = int(time.time())

                scores_update = player.get_all_scores()
                if scores_update != player_data["scores"]:
                    new_scores = {}
                    for i in scores_update:
                        if scores_update[i] != "undefined" and int(scores_update[i]) != int(player_data["scores"][i]):
                            new_scores[i] = scores_update[i]

                    last_scores = player_data["scores"].copy()
                    player_data["scores"] = scores_update
                
                    channel = discord.utils.get(self.bot.get_all_channels(), id=945705987833233418)
                
                for i in current_data:
                    KnownPlayers.data[i] = current_data[i]

                KnownPlayers.save_data()
                current_data = KnownPlayers.get_data()

                await sheet.update_sheet(guild_data, player_data, last_scores, new_scores, channel)

                await asyncio.sleep(4) #TODO: changer le temps en fonction du nombre de requetes max par minutes
            
            current_data[i_player_data] = player_data
    

    @update_players_data.before_loop
    async def before_update_players_data(self):
        print('waiting...')
        await self.bot.wait_until_ready()


def setup(bot):
    # bot.add_cog(BotLoops(bot))
    pass