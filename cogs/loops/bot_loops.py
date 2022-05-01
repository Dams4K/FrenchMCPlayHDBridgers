import asyncio, time, discord
from discord.ext import commands, tasks
from utils.bot_data import BaseData, KnownPlayers, Player, GuildData, get_current_status, LeaderboardSheet
from utils.lang.lang import Lang
from utils.references import References
from utils.bot_logging import get_logging

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
                await self.bot.sync_commands(guild_ids=[guild_id], unregister_guilds=[guild_id])


    @tasks.loop(seconds=600)
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
                n_scores = KnownPlayers.update_player(player)

                if n_scores != False:
                    for g in self.bot.guilds:
                        g_data = GuildData(g.id)

                        if not player.uuid in g_data.whitelist.data: continue

                        if any(e in n_scores.keys() for e in ["short", "normal"]):
                            last_pos, new_pos = g_data.sheet.update_player(player, LeaderboardSheet.GLOBAL_SHEET)
                            p_discord_id = g_data.whitelist.data[player.uuid]

                            printable_modes = [ e for e in list(n_scores.keys()) if e in ["short", "normal"] ]

                            kwargs = {
                                "member_mention": f"<@{p_discord_id}>" if p_discord_id != None else player.name,
                                "last_pos": last_pos,
                                "new_pos": new_pos,
                                "str_new_global_score": format(player.global_score/1000, ".3f"),
                                "mode": "** & **".join(printable_modes),
                                "score": "** & **".join([str(format(n_scores[e]/1000, ".3f")) for e in printable_modes]),
                            }

                            print(last_pos, new_pos)

                            if last_pos == new_pos == False: continue # si le lb n'a pas été update
                            if player.normal >= LeaderboardSheet.NORMAL_SUB_TIME: continue # si le joueur n'a pas sub 12 en normal

                            channel = discord.utils.get(self.bot.get_all_channels(), id=g_data.get_pb_channel())

                            if last_pos == new_pos or -1 in [last_pos, new_pos]:
                                await channel.send(Lang.get_text("SAME_PB", "fr", **kwargs))
                                pass
                            elif last_pos > new_pos:
                                await channel.send(Lang.get_text("BETTER_PB", "fr", **kwargs))

                        
                        for sheet in LeaderboardSheet.SHEETS:
                            print(sheet)
                            if sheet == LeaderboardSheet.GLOBAL_SHEET: continue

                            g_data.sheet.update_player(player, sheet)
                
                await asyncio.sleep(sleep_time_betwen_player_update * 4 + 1)
    
    
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
        KnownPlayers.data[p_uuid] = player.to_dict()
        KnownPlayers.save_data()
        await asyncio.sleep(5*60)
    

    @update_name.before_loop
    async def before_update_name(self):
        print('update name loop started')
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(BotLoops(bot))
    pass