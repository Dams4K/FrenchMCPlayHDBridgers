from discord.ext import commands
from utils.references import References

def is_the_author(ctx: commands.Context):
    return ctx.author.id in References.AUTHORS_ID


def can_moderate(ctx):
    return is_the_author(ctx) or ctx.author.guild_permissions.administrator