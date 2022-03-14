import discord
from discord.commands import permissions, slash_command, user_command
from discord.commands import SlashCommandGroup, UserCommand
from discord import Option
from discord.commands.context import ApplicationContext
from discord.ext import commands, pages

from utils.references import References
from utils.bot_data import Player
from utils.bot_data import *
from utils.checks import *
from utils.overwriting import *

import time

class WhiteListCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.base_page: discord.Embed = discord.Embed(
            title=Lang.get_text("WHITELIST_LIST", "fr"),
            color=0xffffff
        )


    def cog_check(self, ctx: commands.Context):
        return can_moderate(ctx)


    def get_pages(self, ctx: BotApplicationContext):
        whitelist_data = ctx.guild_data.whitelist.get_data()
        pages = []

        MAX_PLAYER_IN_PAGE = 15

        for i in range(int(len(whitelist_data)/MAX_PLAYER_IN_PAGE)+1):
            new_page = self.base_page.copy()
            description = ""
            for j in range(i*MAX_PLAYER_IN_PAGE, min(int((i+1)*MAX_PLAYER_IN_PAGE), len(whitelist_data))):
                uuid = list(whitelist_data.keys())[j]
                player = Player(uuid=uuid)
                member = discord.utils.get(self.bot.get_all_members(), id=whitelist_data[uuid])
                description += Lang.get_text("BASE_WHITELIST_LIST_PLAYER", "fr", name=player.name, member=member) + "\n"

            new_page.description = description
            pages.append(new_page)
        return pages


    # SLASH_COMMANDS
    whitelist = SlashCommandGroup(
        "whitelist", "Comme ça le joueur sera dans le leaderbord :)", guild_ids=References.BETA_GUILDS
    )
    whitelist.checks = [can_moderate]

    @whitelist.command(name="add", guild_ids=References.BETA_GUILDS)
    async def whitelist_add_player(
        self, ctx,
        member: Option(discord.Member, "member", required=True),
        name: Option(str, "player_name", required=False) = None,
        uuid: Option(str, "player_uuid", required=False) = None
    ):
        if uuid == name == None: name = member.nick if member.nick else member.name

        response_args = ctx.guild_data.whitelist.add_player(member=member, name=name, uuid=uuid)
        await ctx.respond(**response_args)


    @whitelist.command(name="remove", guild_ids=References.BETA_GUILDS)
    async def whitelist_remove_player(self, ctx,
        member: Option(discord.Member, "member", required=False) = None,
        name: Option(str, "player_name", required=False) = None,
        uuid: Option(str, "player_name", required=False) = None
    ):
        if uuid == name == None and member != None: name = member.nick if member.nick else member.name
        
        response_args = ctx.guild_data.whitelist.remove_player(member=member, name=name, uuid=uuid)
        await ctx.respond(**response_args)
        

    @whitelist.command(name="list", description="List of whitelisted players", guild_ids=References.BETA_GUILDS)
    async def whitelist_list(self, ctx):
        paginator = pages.Paginator(pages=self.get_pages(ctx), show_disabled=False, loop_pages=True)
        await paginator.respond(ctx.interaction)


    # @commands.command(name="whitelist_add")
    # async def _whitelist_add(self, ctx, member: discord.Member, name: str = None, uuid: str = None):
    #     if uuid == name == None: name = member.nick if member.nick else member.name

    #     guild_data = GuildData(ctx.guild.id)
    #     response_args = guild_data.whitelist.add_player(member=member, name=name, uuid=uuid)
    #     await ctx.send(**response_args)


    # @commands.command(name="whitelist_remove")
    # async def _whitelist_add(self, ctx, member: discord.Member = None, name: str = None, uuid: str = None):
    #     if uuid == name == None and member != None: name = member.nick if member.nick else member.name

    #     guild_data = GuildData(ctx.guild.id)
    #     response_args = guild_data.whitelist.remove_player(member=member, name=name, uuid=uuid)
    #     await ctx.send(**response_args)


    # @commands.command(name="whitelist_list")
    # async def whitelist_list(self, ctx):
    #     guild_data = GuildData(ctx.guild.id)
    #     paginator = pages.Paginator(pages=self.get_pages(ctx), show_disabled=False, loop_pages=True)
    #     await paginator.send(ctx.interaction)


    # USER_COMMANDS
    @user_command(name="Whitelist Add Member", guild_ids=References.BETA_GUILDS)
    async def user_whitelist_add_player(self, ctx, member: discord.Member):
        await self.whitelist_add_player(self, ctx, member=member)
    @user_command(name="Whitelist Remove Member", guild_ids=References.BETA_GUILDS)
    async def user_whitelist_remove_player(self, ctx, member: discord.Member):
        await self.whitelist_remove_player(self, ctx, member=member)
    

def setup(bot):
    bot.add_cog(WhiteListCommands(bot))