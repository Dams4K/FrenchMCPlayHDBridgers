import discord
from discord import slash_command
from discord.ext import commands
from utils.references import References
from utils.bot_data import Player
from utils.bot_data import *
from utils.checks import *
import time

class WhiteListCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context):
        return is_the_author(ctx) or ctx.guild.owner_id == ctx.author.id


    @slash_command(
        base="whitelist", name="add", description="Add player to the whitelist",
        guild_ids=References.BETA_GUILDS,
        options=[
            create_option(
                name="member", description="give member chacal",
                option_type=SlashCommandOptionType.USER, required=True
            ),
            create_option(
                name="name", description="give minecraft player name",
                option_type=SlashCommandOptionType.STRING, required=False
            ), create_option(
                name="uuid", description="give minecraft player uuid",
                option_type=SlashCommandOptionType.STRING, required=False
            )
        ])
    async def _whitelist_add_command(self, ctx: SlashContext, **kwargs):
        guild_data = GuildData(ctx.guild.id)
        if not ("uuid" and "name") in kwargs:
            kwargs["name"] = kwargs.get("member").name
        msg = guild_data.whitelist.add_player(**kwargs)

        await ctx.send(msg)


    @cog_ext.cog_subcommand(
        base="whitelist", name="remove", description="Add player to the whitelist",
        guild_ids=References.BETA_GUILDS,
        options=[
            create_option(
                name="member", description="give member chacal",
                option_type=SlashCommandOptionType.USER, required=False
            ),
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
        if not ("uuid" and "name") in kwargs:
            kwargs["name"] = kwargs.get("member").name
        guild_data.whitelist.remove_player(**kwargs)

        await ctx.send(Lang.get_text("PLAYER_REMOVED_FROM_WHITELIST", "fr"))
        

    @cog_ext.cog_subcommand(
        base="whitelist", name="list", description="Add player to the whitelist",
        guild_ids=References.BETA_GUILDS)
    async def _whitelist_list_command(self, ctx: SlashContext):
        msg = await ctx.send("load whitelist")
        new_content = GuildData(ctx.guild.id).whitelist.player_list()
        await msg.edit(content=new_content)

def setup(bot):
    bot.add_cog(WhiteListCommands(bot))