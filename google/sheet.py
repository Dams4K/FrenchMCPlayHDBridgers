from utils.references import References
from utils.bot_data import KnownPlayers, GuildData, Player
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from utils.lang.lang import Lang

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

    def __init__(self):
        self.credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        self.SAMPLE_SPREADSHEET_ID = References.WORKSHEET_ID
        self.service = build('sheets', 'v4', credentials=self.credentials)
        self.sheet = self.service.spreadsheets()
    
    def calc_global_score(self, scores: dict):
        if isinstance(scores["normal"], int) and scores["normal"] > 0 and isinstance(scores["short"], int) and scores["short"] > 0:
            return int(round(scores["normal"] / 2 + scores["short"], 3))

    async def update_sheet(self, guilds_data, player: Player, l_scores):
        for guild_data in guilds_data:
            member_id = guild_data.whitelist.data[player.uuid]
            spreadsheet_id = guild_data.get_spreadsheet_id()
            if spreadsheet_id == None:
                print("spreadsheet_id is None")
                continue

            new_scores = player.scores
            if self.GLOBAL_MODES.intersection(set(new_scores)):
                l_sheet_values = self.sheet.values().get(spreadsheetId=spreadsheet_id, range=self.GLOBAL_RANGE).execute().get("values", [])
                if self.INCLINED_MODE in new_scores: new_scores.pop(self.INCLINED_MODE)
                if self.ONESTACK_MODE in new_scores: new_scores.pop(self.ONESTACK_MODE)
                n_leaderboard = await self.update_global_sheet(guild_data, l_sheet_values, player, new_scores, l_scores, guilds_data[guild_data], member_id)
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


    async def update_global_sheet(self, guild_data, l_sheet_values, player, new_scores, l_scores, channel, member_id):
        l_leaderboard = self.parse_global_leaderboard(l_sheet_values)
        l_global_score = self.calc_global_score(l_scores)
        n_leaderboard = self.get_global_leaderboard(guild_data)
        
        n_global_score = self.calc_global_score(new_scores)
        print(n_global_score)
        print(player.scores["short"])
        if n_global_score == None or player.scores["short"] == None or player.scores["short"] > 6000: return

        l_player_pos = -1
        for p_data in l_leaderboard.get(l_global_score, []):
            if p_data["name"] == player.name:
                l_player_pos = list(l_leaderboard.keys()).index(l_global_score)

        
        n_player_pos = -1
        
        for p_data in n_leaderboard.get(n_global_score, []):
            if p_data["name"] == player.name:
                n_player_pos = list(n_leaderboard.keys()).index(n_global_score)
                
        modes = list(new_scores.keys())
        new_scores = list(new_scores.values())
        new_scores = [format(e/1000, ".3f") for e in new_scores]
        get_test_kwargs = {
            "member_id": member_id,
            "last_pos": l_player_pos,
            "new_pos": n_player_pos,
            "str_new_global_score": format(n_global_score/1000, ".3f"),
            "mode": "** & **".join(modes),
            "score": "** & **".join(new_scores),
        }

        if l_player_pos < n_player_pos and l_player_pos != -1:
            await channel.send(Lang.get_text("BETTER_PB", "fr", **get_test_kwargs))
        elif l_player_pos == n_player_pos or l_player_pos == -1:
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
                    "short": float(player_infos[5]),
                    "normal": float(player_infos[4]),
                })
        return leaderboard
    

    def get_global_leaderboard(self, guild_data: GuildData):
        leaderboard = {None: []}
        
        for uuid in guild_data.whitelist.data:
            player = Player(uuid=uuid)
            if player == None: continue
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