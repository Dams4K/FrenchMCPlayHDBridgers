from bot import LeaderboardBot
from utils.references import References
from utils.lang.lang import Lang

bot = LeaderboardBot()

# bot.load_cogs(References.COGS_FOLDER)

@bot.slash

bot.run(References.BOT_TOKEN)