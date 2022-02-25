from bot import LeaderboardBot
from utils.references import References
from discord_slash import SlashCommand

bot = LeaderboardBot()
slash = SlashCommand(bot, sync_commands=True)

bot.load_cogs(References.COGS_FOLDER)

bot.run(References.BOT_TOKEN)