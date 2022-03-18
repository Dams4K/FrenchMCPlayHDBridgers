import asyncio, time, discord
from discord.ext import commands, tasks
from utils.bot_data import BaseData, KnownPlayers, Player, GuildData, get_current_status
from google.sheet import LeaderboardSheet
from utils.references import References

class BotLoops(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.update_players.start()
        self.update_name.start()
        self.desynced_commands.start()


    @tasks.loop(seconds=20)
    async def desynced_commands(self):
        for guild_id in References.BETA_GUILDS:
            g_desynced_commands = await self.bot.get_desynced_commands(guild_id=guild_id)
            if g_desynced_commands:
                # print("resync", guild_id, g_desynced_commands)
                await self.bot.sync_commands(guild_ids=[guild_id], unregister_guilds=[guild_id])


    @tasks.loop(seconds=1200)
    async def update_players(self):
        for g in self.bot.guilds:
            g_data = GuildData(g.id)
            for p_uuid in g_data.whitelist.data:
                Player(uuid=p_uuid)

        KnownPlayers.load_data()
        current_data = KnownPlayers.get_data()

        mcplayhd_api_status = get_current_status()["data"]["user"]
        sleep_time_betwen_player_update = mcplayhd_api_status["rateLimitTimeMs"] / 1000 / mcplayhd_api_status["rateLimit"]

        for p_uuid in current_data:
            player = Player(uuid=p_uuid)
            if int(time.time()) - player.last_update > self.update_players._sleep:
                l_scores = player.scores.copy()
                new_scores = KnownPlayers.update_player(p_uuid)
                if new_scores:
                    for mode in new_scores:
                        player.scores[mode] = new_scores[mode]
                    guilds_data = {}
                    for g in self.bot.guilds:
                        g_data = GuildData(g.id)
                        if not player.uuid in g_data.whitelist.data: continue
                        ch = discord.utils.get(self.bot.get_all_channels(), id=g_data.get_pb_channel())
                        if not ch: continue
                    
                        guilds_data[g_data] = ch
                    await LeaderboardSheet.update_sheet(guilds_data, player, l_scores, new_scores)
                await asyncio.sleep(sleep_time_betwen_player_update * 4 + 4)
    
    
    @update_players.before_loop
    async def before_update_players(self):
        print('update players loop started')
        await self.bot.wait_until_ready()


    @tasks.loop(hours=1)
    async def update_name(self):
        KnownPlayers.load_data()
        current_data = KnownPlayers.get_data()

        for p_uuid in current_data:
            player = Player(uuid=p_uuid)
            player.name = player.uuid_to_name()
        
        KnownPlayers.load_data()
        KnownPlayers.data[uuid] = player.to_dict()
        KnownPlayers.save_data()
        await asyncio.sleep(5*60)
    

    @update_name.before_loop
    async def before_update_name(self):
        print('update name loop started')
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(BotLoops(bot))
    pass