from utils.references import References
from utils.bot_data import KnownPlayers, GuildData, Player
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from utils.lang.lang import Lang
from utils.bot_logging import get_logging

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'datas/google_keys.json'

SAMPLE_RANGE_NAME = "Global (Bot)!A1:F"

def calc_global_score(scores: dict):
    if isinstance(scores["normal"], int) and scores["normal"] > 0 and isinstance(scores["short"], int) and scores["short"] > 0:
        return int(round(scores["normal"] / 2 + scores["short"], 3))


class _LeaderboardSheet:
    GLOBAL_RANGE = "Global (Bot)!A1:F"
    ONESTACK_RANGE = ""
    INCLINED_RANGE = ""

    GLOBAL_MODES = {"normal", "short"}
    INCLINED_MODE = "inclined"
    ONESTACK_MODE = "onestack"

    logging_error = get_logging(__name__, "error")
    logging_debug = get_logging(__name__, "debug")
    
    def __init__(self):
        self.credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        self.SAMPLE_SPREADSHEET_ID = References.WORKSHEET_ID
        self.service = build('sheets', 'v4', credentials=self.credentials)
        self.sheet = self.service.spreadsheets()
    
    def calc_global_score(self, scores: dict):
        if isinstance(scores["normal"], int) and scores["normal"] > 0 and isinstance(scores["short"], int) and scores["short"] > 0:
            return int(round(scores["normal"] / 2 + scores["short"], 3))

    async def update_sheet(self, guilds_data, player: Player, l_scores, new_scores):
        for guild_data in guilds_data:
            member_id = guild_data.whitelist.data[player.uuid]

            spreadsheet_id = guild_data.get_spreadsheet_id()
            if spreadsheet_id == None:
                self.logging_error.error(f"spreadsheet_id is None fo {guild_data.id}")
                continue

            if self.GLOBAL_MODES.intersection(set(new_scores)):
                if self.INCLINED_MODE in new_scores: new_scores.pop(self.INCLINED_MODE)
                if self.ONESTACK_MODE in new_scores: new_scores.pop(self.ONESTACK_MODE)
                if player.scores["short"] != None and player.scores["short"] != -1 and player.scores["short"] < 6000:
                    n_leaderboard = await self.update_global_sheet(guild_data, player, new_scores, l_scores, guilds_data[guild_data], member_id, player.scores)
                    
                    self.logging_debug.debug(n_leaderboard)

                    if n_leaderboard:
                        self.sheet.values().clear(spreadsheetId=spreadsheet_id, range=self.GLOBAL_RANGE).execute()
                        request = self.sheet.values().update(
                            spreadsheetId=spreadsheet_id, range=self.GLOBAL_RANGE,
                            valueInputOption="USER_ENTERED", body={"values": self.gen_leaderboard(n_leaderboard) }
                        ).execute()
            
            if self.INCLINED_MODE in new_scores:
                pass
            if self.ONESTACK_MODE in new_scores:
                pass


    async def update_global_sheet(self, guild_data, player, new_scores, l_scores, channel, member_id, scores):
        spreadsheet_id = guild_data.get_spreadsheet_id()
        l_sheet_values = self.sheet.values().get(spreadsheetId=spreadsheet_id, range=self.GLOBAL_RANGE).execute().get("values", [])
        
        l_leaderboard = self.parse_global_leaderboard(l_sheet_values)
        
        self.logging_debug.debug(member_id)

        l_global_score = self.calc_global_score(l_scores)
        n_leaderboard = self.get_global_leaderboard(guild_data)
        
        n_global_score = self.calc_global_score(scores)
        
        if n_global_score == None: return False


        l_best_times = list(l_leaderboard.keys())
        if None in l_best_times: l_best_times.remove(None)
        l_best_times.sort()
        gap, l_player_pos, find = 0, -1, False

        for i in range(len(l_best_times)):
            l_player_pos = i+1+gap
            for player_data in l_leaderboard[l_best_times[i]]:
                if player_data["name"] == player.name: find = True
            if find: break
            gap += len(l_leaderboard[l_best_times[i]])-1

        n_best_times = list(n_leaderboard.keys())
        if None in n_best_times: n_best_times.remove(None)
        
        n_best_times.sort()
        gap, n_player_pos, find = 0, -1, False
        
        for i in range(len(n_best_times)):
            n_player_pos = i+1+gap
            for player_data in n_leaderboard[n_best_times[i]]:
                if player_data["name"] == player.name: find = True
            if find: break
            gap += len(n_leaderboard[n_best_times[i]])-1

        modes = list(new_scores.keys())
        _new_scores = list(new_scores.values())
        _new_scores = [format(e/1000, ".3f") for e in _new_scores]
        get_test_kwargs = {
            "member_mention": f"<@{member_id}>" if isinstance(member_id, int) else player.name,
            "last_pos": l_player_pos,
            "new_pos": n_player_pos,
            "str_new_global_score": format(n_global_score/1000, ".3f"),
            "mode": "** & **".join(modes),
            "score": "** & **".join(_new_scores),
        }
        # le bot ne regarde pas si il y a 2 personnes à la meme position et du coup il dit 24 au lieu de 26
        self.logging_debug.debug(f"last: {l_player_pos} -> new: {n_player_pos}; member_id: {member_id if member_id == None else player.name}")
        if l_player_pos > n_player_pos and l_player_pos != -1 and -1 < new_scores.get("normal", -1) < 12000:
            msg = await channel.send(Lang.get_text("BETTER_PB", "fr", **get_test_kwargs))
            self.logging_debug.debug(f"better pb send (message id: {msg.id}) for player {member_id if member_id == None else player.name}")
        elif l_player_pos == n_player_pos or l_player_pos == -1 and -1 < new_scores.get("normal", -1) < 12000:
            await channel.send(Lang.get_text("SAME_PB", "fr", **get_test_kwargs))


        return n_leaderboard
                

    def parse_global_leaderboard(self, values):
        leaderboard = {}
        if values != []:
            values.pop(0)
            for player_infos in values:
                if player_infos == []:
                    continue
                global_score = int(float(player_infos[2])*1000)
                leaderboard.setdefault(global_score, [])

                leaderboard[global_score].append({
                    "name": player_infos[1],
                    "short": float(player_infos[5].replace(",", ".")),
                    "normal": float(player_infos[4].replace(",", ".")),
                })
        return leaderboard
    

    def get_global_leaderboard(self, guild_data: GuildData):
        leaderboard = {None: []}
        
        for uuid in guild_data.whitelist.data:
            player = Player(uuid=uuid)
            if player == None or player.scores["short"] == None or player.scores["short"] >= 6000: continue
            global_score = calc_global_score(player.scores)
            if global_score == None: continue

            leaderboard.setdefault(global_score, [])

            short = format(player.scores["short"]/1000, ".3f") if player.scores["short"]/1000 != "undefined" else -1
            normal = format(player.scores["normal"]/1000, ".3f") if player.scores["normal"]/1000 != "undefined" else -1

            leaderboard[global_score].append({
                "name": player.name,
                "short": short,
                "normal": normal,
            })
        
        return leaderboard

    def gen_leaderboard(self, leaderboard):
        if not leaderboard: return None
        best_times = list(leaderboard.keys())
        best_times.remove(None)
        best_times.sort()

        values = [["Classement", "Pseudo", "Normal/2 + Short", "", "Normal", "Short"]]

        msg = ""
        gap = 0

        for i in range(len(best_times)):
            pos = i+1+gap
            for player_data in leaderboard[best_times[i]]:
                values.append(["#" + str(pos), player_data["name"], format(best_times[i]/1000, ".3f"), "", player_data["normal"], player_data["short"]])
            gap += len(leaderboard[best_times[i]])-1

        return values

LeaderboardSheet: _LeaderboardSheet = _LeaderboardSheet()