import discord
from discord import Option
from discord.ext import commands
from discord.commands import permissions, slash_command
from utils.bot_data import *
from utils.references import References
from utils.overwriting import BotApplicationContext
from utils.lang.lang import Lang
from utils.checks import *
from discord.ext import bridge

class GlobalAdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print(__name__, "on")


    @slash_command(name="set_new_pb_channel", checks=[can_moderate], guild_ids=References.BETA_GUILDS)
    async def set_new_pb_channel(
        self, ctx: BotApplicationContext, 
        channel: Option(discord.TextChannel, "channel", required=True)
    ):
        ctx.guild_data.set_pb_channel(channel.id)
        await ctx.respond(Lang.get_text("NEW_PB_CHANNEL_CHANGE", "fr", channel=channel))


    @slash_command(name="update_sheet", checks=[can_moderate], guild_ids=References.BETA_GUILDS)
    async def update_sheet(self, ctx, sheet_name: Option(str, "sheet_name", required=True, choices=["global", "normal", "short", "inclined", "onestack", "inclinedshort"])):
        sheet = getattr(LeaderboardSheet, sheet_name.upper() + "_SHEET")
        ctx.guild_data.sheet.update_sheet(sheet, ctx.guild_data.sheet.gen_leaderboard(sheet))
        await ctx.respond("google sheet mis-à-jour")
    

    @slash_command(name="send_pb", checks=[can_moderate], guild_ids=References.BETA_GUILDS)
    async def send_pb(
        self, ctx,
        player_name: Option(str, "player_name", required=True) = None,
        normal_time: Option(float, "normal_time", required=False) = -1,
        short_time: Option(float, "short_time", required=False) = -1
    ):
        if not player_name: return

        player_discord_id = None
        player = None

        for uuid in KnownPlayers.data:
            if KnownPlayers.data[uuid]["name"].lower() == player_name.lower():
                guild_players = ctx.guild_data.whitelist.data
                if uuid in guild_players: player_discord_id = ctx.guild_data.whitelist.data[uuid]

                player = Player(uuid=uuid)
        if not player: return

        member = discord.utils.get(ctx.guild.members, id=player_discord_id)
        member_mention = member.mention if member else player_name

        channel_id = ctx.guild_data.get_pb_channel()
        channel = discord.utils.get(ctx.guild.text_channels, id=channel_id)

        player.scores["short"] = short_time if short_time else -1
        player.scores["normal"] = normal_time if normal_time else -1

        modes = []
        scores = []
        if normal_time >= 0:
            modes.append("normal")
            scores.append(format(normal_time, ".3f"))
        if short_time >= 0:
            modes.append("short")
            scores.append(format(short_time, ".3f"))
            
        kwargs = {
            "member_mention": member_mention,
            "mode": "** & **".join(modes),
            "score": "** & **".join(scores),
            "str_new_global_score": format(player.global_score, ".3f"),
            "new_pos": ctx.guild_data.sheet.get_player_pos(player, ctx.guild_data.sheet.gen_leaderboard(LeaderboardSheet.GLOBAL_SHEET, players_overrider=[player]))
        }

        print(kwargs)

        if normal_time > 0: await channel.send(Lang.get_text("SAME_PB", "fr", **kwargs))
        if short_time > 0: await channel.send(Lang.get_text("SAME_PB", "fr", **kwargs))

        await ctx.respond("pb sent")


def setup(bot):
    bot.add_cog(GlobalAdminCommands(bot))