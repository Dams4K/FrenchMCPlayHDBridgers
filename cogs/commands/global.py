import discord
import os
from discord import Option
from discord.ext import commands
from discord.commands import permissions
from utils.references import References
from utils.bot_data import Player, LeaderboardSheet
from discord.ext import bridge

class GlobalUserCommands(commands.Cog):
    rank_emojis = [
        "<:First:979371544092475422>",
        "<:Second:979371577890185296>",
        "<:Third:979371618210041867>"
    ]

    def __init__(self, bot):
        self.bot = bot
        print(__name__, "on")


    @bridge.bridge_command(name="hello")
    async def hello_world(self, ctx):
        await ctx.respond("world")


    @bridge.bridge_command(name="testpb")
    async def test_pb_command(self, ctx,
        member: Option(discord.Member, "member", required=False) = None,
        player_name: Option(str, "player_name", required=False) = None,
        normal: Option(float, "normal", required=False) = None,
        short: Option(float, "short", required=False) = None,
        inclined: Option(float, "inclined", required=False) = None,
        onestack: Option(float, "onestack", required=False) = None
    ):
        g_sheet = ctx.guild_data.sheet
        player = None
        
        if member != None:
            w_data = guild_data.whitelist.get_data()
            for p_uuid in w_data:
                if member.id == w_data[p_uuid]:
                    player = Player(uuid=p_uuid)
        elif player_name != None:
            try:
                player = Player(name=player_name)
            except:
                pass

        if player == None:
            player = Player(faked=True)
        
        if normal != None: player.scores["normal"] = int(round(normal, 3) * 1000)
        if short != None: player.scores["short"] = int(round(short, 3) * 1000)
        if inclined != None: player.scores["inclined"] = int(round(inclined, 3) * 1000)
        if onestack != None: player.scores["onestack"] = int(round(onestack, 3) * 1000)

        embed = discord.Embed(title=f"Position hypothétique de **{player.name if player.name != None else 'personne'}**")
        desc = ""
        for sheet in LeaderboardSheet.SHEETS:

            lb = g_sheet.gen_leaderboard(sheet, players_overrider=[player])
            pos = g_sheet.get_player_pos(player, lb)

            if pos == -1: continue

            sheet_name = sheet.replace(
                LeaderboardSheet.GLOBAL_SHEET, f"**__global__** *({format(player.global_score/1000, '.3f')})*"
            ).replace(
                LeaderboardSheet.NORMAL_SHEET, f"**__normal__** *({format(player.normal/1000, '.3f')})*"
            ).replace(
                LeaderboardSheet.SHORT_SHEET, f"**__short__** *({format(player.short/1000, '.3f')})*"
            ).replace(
                LeaderboardSheet.INCLINED_SHEET, f"**__inclined__** *({format(player.inclined/1000, '.3f')})*"
            ).replace(
                LeaderboardSheet.ONESTACK_SHEET, f"**__onestack__** *({format(player.onestack/1000, '.3f')})*"
            )

            desc += sheet_name + ": " + ("#" + str(pos) if pos > 3 else GlobalUserCommands.rank_emojis[pos-1]) + "\n"
        embed.description = desc
        await ctx.respond(embed=embed)
    
    @bridge.bridge_command(name="stats")
    async def stats_comand(self, ctx):
        os.system("neofetch > neofetch.txt")
        with open("neofetch.txt", "r") as f:
            msg = "".join(f.readlines())
            await ctx.respond("```ansi\n" + msg + "\n```")

def setup(bot):
    bot.add_cog(GlobalUserCommands(bot))