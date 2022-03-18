from bot import LeaderboardBot
from utils.references import References
from utils.lang.lang import Lang
from utils.bot_logging import create_new_log

create_new_log()

bot: LeaderboardBot = LeaderboardBot()

bot.run(References.BOT_TOKEN)