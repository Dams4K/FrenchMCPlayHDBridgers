import discord
from discord_slash import cog_ext, SlashContext
from discord.ext import commands
from discord_slash.utils.manage_commands import create_option, create_choice, create_permission
from discord_slash.model import SlashCommandOptionType, SlashCommandPermissionType
from utils.references import References
from utils.mcplayhd_api import Player
from utils.bot_data import DataActions, Data

class WhiteListCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @cog_ext.cog_subcommand(
        base="whitelist", name="add", description="Add player to the whitelist",
        guild_ids=References.BETA_GUILDS,
        options=[
            create_option(
                name="player_name", description="give minecraft player name (case insensitive)",
                option_type=SlashCommandOptionType.STRING, required=True
            )
        ])
    async def _whitelist_add_command(self, ctx: SlashContext, player_name):
        err, msg = Data.whitelist(action=DataActions.ADD, guild_id=str(ctx.guild.id), player_name=player_name)
        await ctx.send(msg)


    @cog_ext.cog_subcommand(
        base="whitelist", name="remove", description="Add player to the whitelist",
        guild_ids=References.BETA_GUILDS,
        options=[
            create_option(
                name="player_name", description="give minecraft player name (case insensitive)",
                option_type=SlashCommandOptionType.STRING, required=True
            )
        ])
    async def _whitelist_remove_command(self, ctx: SlashContext, player_name):
        err, msg = Data.whitelist(action=DataActions.REMOVE, guild_id=str(ctx.guild.id), player_name=player_name)
        await ctx.send(msg)
    

    @cog_ext.cog_subcommand(
        base="whitelist", name="list", description="Add player to the whitelist",
        guild_ids=References.BETA_GUILDS)
    async def _whitelist_list_command(self, ctx: SlashContext):
        err, msg = Data.whitelist(action=DataActions.LIST, guild_id=str(ctx.guild.id))
        await ctx.send(msg)

def setup(bot):
    bot.add_cog(WhiteListCommands(bot))