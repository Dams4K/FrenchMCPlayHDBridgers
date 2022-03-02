from discord.ext import commands
from utils.references import References

def is_the_author(ctx: commands.Context):
    return ctx.author.id in References.AUTHORS_ID