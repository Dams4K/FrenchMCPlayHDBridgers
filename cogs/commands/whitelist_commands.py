import discord
from discord_slash import cog_ext, SlashContext
from discord.ext import commands
from discord_slash.utils.manage_commands import create_option, create_choice, create_permission
from discord_slash.model import SlashCommandOptionType, SlashCommandPermissionType
from utils.references import References
from utils.mcplayhd_api import Player
from utils.bot_data import *

class WhiteListCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @cog_ext.cog_subcommand(
        base="whitelist", name="add", description="Add player to the whitelist",
        guild_ids=References.BETA_GUILDS,
        options=[
            create_option(
                name="name", description="give minecraft player name",
                option_type=SlashCommandOptionType.STRING, required=False
            ), create_option(
                name="uuid", description="give minecraft player uuid",
                option_type=SlashCommandOptionType.STRING, required=False
            ),
        ])
    async def _whitelist_add_command(self, ctx: SlashContext, **kwargs):
        guild_data = GuildData(ctx.guild.id)
        guild_data.whitelist.add_player(**kwargs)


    @cog_ext.cog_subcommand(
        base="whitelist", name="remove", description="Add player to the whitelist",
        guild_ids=References.BETA_GUILDS,
        options=[
            create_option(
                name="name", description="give minecraft player name",
                option_type=SlashCommandOptionType.STRING, required=False
            ), create_option(
                name="uuid", description="give minecraft player uuid",
                option_type=SlashCommandOptionType.STRING, required=False
            ),
        ])
    async def _whitelist_remove_command(self, ctx: SlashContext, **kwargs):
        guild_data = GuildData(ctx.guild.id)
        guild_data.whitelist.remove_player(**kwargs)
        

    @cog_ext.cog_subcommand(
        base="whitelist", name="list", description="Add player to the whitelist",
        guild_ids=References.BETA_GUILDS)
    async def _whitelist_list_command(self, ctx: SlashContext):
        err, msg = Data.whitelist(action=DataActions.LIST, guild_id=str(ctx.guild.id))
        await ctx.send(msg)

def setup(bot):
    bot.add_cog(WhiteListCommands(bot))