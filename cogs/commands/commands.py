import discord
from discord.ext import commands
from utils.references import References
from utils.bot_data import Player

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    

    @cog_ext.cog_slash(
        name="update", description="Manually update the leaderboard",
        guild_ids=References.BETA_GUILDS,
        permissions={
            912435770290229348: [
                create_permission(320331197836427276, SlashCommandPermissionType.USER, True)
            ]
        })
    async def _update_command(self, ctx: SlashContext):
        await ctx.send("start update")


    @cog_ext.cog_slash(
        name="lang", description="Select the language you want",
        guild_ids=References.BETA_GUILDS,
        options=[
            create_option(
                name="lang",
                description="first option",
                required=True,
                option_type=3, 
                choices=[
                    create_choice(value="en", name="English"),
                    create_choice(value="fr", name="Français")
                ]
            )
        ])
    async def _lang(self, ctx: SlashContext, lang: str):
        # Data.set_lang(str(ctx.guild.id), lang)
        await ctx.send(lang)
    

def setup(bot):
    bot.add_cog(Commands(bot))