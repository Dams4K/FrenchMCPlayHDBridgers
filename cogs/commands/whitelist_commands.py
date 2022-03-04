import discord
from discord.commands import SlashCommandGroup
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

    async def cog_check(self, ctx: commands.Context):
        return is_the_author(ctx) or ctx.guild.owner_id == ctx.author.id

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
                description += Lang.get_text("BASE_WHITELIST_LIST_PLAYER", "fr", name=player.name) + "\n"

            new_page.description = description
            pages.append(new_page)
        return pages


    whitelist = SlashCommandGroup("whitelist", "Comme ça le joueur sera dans le leaderbord :)")


    @whitelist.command(name="add")
    async def whitelist_add_player(
        self, ctx,
        member: Option(discord.Member, "member", required=True),
        name: Option(str, "player_name"),
        uuid: Option(str, "player_name")
    ):
        if uuid == name == None: name = member.name

        response_args = ctx.guild_data.whitelist.add_player(member=member, name=name, uuid=uuid)
        await ctx.respond(**response_args)


    @whitelist.command(name="remove")
    async def whitelist_remove_player(self, ctx,
        member: Option(discord.Member, "member"),
        name: Option(str, "player_name"),
        uuid: Option(str, "player_name")
    ):
        if uuid == name == None and member != None: name = member.name
        
        response_args = ctx.guild_data.whitelist.remove_player(member=member, name=name, uuid=uuid)
        await ctx.respond(**response_args)
        

    @whitelist.command(name="list")
    async def whitelist_list(self, ctx):
        paginator = pages.Paginator(pages=self.get_pages(ctx), show_disabled=False)
        await paginator.respond(ctx.interaction)

def setup(bot):
    bot.add_cog(WhiteListCommands(bot))