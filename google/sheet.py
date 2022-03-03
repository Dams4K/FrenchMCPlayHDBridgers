from utils.references import References
from utils.bot_data import KnownPlayers, GuildData, Player
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'datas/google_keys.json'

SAMPLE_RANGE_NAME = "Global (Bot)!A1:F"


def calc_global_score(scores: dict):
    if isinstance(scores["normal"], int) and scores["normal"] > 0 and isinstance(scores["short"], int) and scores["short"] > 0:
        return int(round(scores["normal"] / 2 + scores["short"], 3))


async def update_sheet(guild_data: GuildData, player_data, last_scores, new_scores, channel):
    credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)


    SAMPLE_SPREADSHEET_ID = References.WORKSHEET_ID

    try:
        service = build('sheets', 'v4', credentials=credentials)
        sheet = service.spreadsheets()

        player_uuid = player_data["uuid"]
        new_leaderboard = get_leaderboard(guild_data)

        # SEND MESSAGE
        if "short" in new_scores or "normal" in new_leaderboard:
            last_global_score = calc_global_score(last_scores)

            last_values = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME).execute()
            last_leaderboard = parse_leaderboard(last_values.get("values", []))
            last_best_times = list(last_leaderboard.keys())

            last_pos = -1
            if last_global_score in last_best_times: 
                last_pos = last_best_times.index(last_global_score)+1

            new_global_score = calc_global_score(player_data["scores"])
            new_best_times = list(new_leaderboard.keys())

            new_pos = new_best_times.index(new_global_score)+1

            member_id = guild_data.whitelist.data.get(player_uuid)
            for mode in new_scores:
                if mode in ("normal", "short"):
                    str_new_global_score = format(new_global_score/1000, ".3f")
                    score = format(new_scores[mode]/1000, ".3f")
                    if new_pos == last_pos or last_pos == -1:
                        await channel.send(f"**Nouveau PB!** <@{member_id}> {score} en {mode} GG\n#{new_pos} ({str_new_global_score})")
                    elif new_pos > last_pos:
                        await channel.send(f"**Nouveau PB!** <@{member_id}> {score} en {mode} GG\n#{last_pos} -> #{new_pos} ({str_new_global_score})")
                    elif new_pos < last_pos:
                        await channel.send(f"**Nouveau PB!!!!!!!** Ah bah nan enfaite, <@{member_id}> a décidé de faire je ne sais quoi, mais son pb a diminué.... Donc.. son nouveau pb... est de {score} en {mode} GG!!!??......\n#{last_pos} -> #{new_pos} ({str_new_global_score})")
            
                

            

        # CLEAR AND UPDATE SHEET
        sheet.values().clear(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME).execute()

        request = sheet.values().update(
            spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Global (Bot)!A1",
            valueInputOption="USER_ENTERED", body={"values": gen_leaderboard(new_leaderboard) }
        ).execute()
        print(request)
    except HttpError as err:
        print(err)


def parse_leaderboard(values):
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


def get_leaderboard(guild_data: GuildData):
    global_players_data = KnownPlayers.get_data()

    leaderboard = {None: []}
    
    for uuid in guild_data.whitelist.data:
        if not uuid in KnownPlayers.data:
            KnownPlayers.add_player(Player(uuid=uuid))
            
        player_data = global_players_data.get(uuid, None)

        if player_data == None: continue

        global_score = calc_global_score(player_data["scores"])
        leaderboard.setdefault(global_score, [])

        print(player_data["scores"]["short"])
        short = format(player_data["scores"]["short"]/1000, ".3f") if player_data["scores"]["short"]/1000 != "undefined" else -1
        normal = format(player_data["scores"]["normal"]/1000, ".3f") if player_data["scores"]["normal"]/1000 != "undefined" else -1

        leaderboard[global_score].append({
            "name": player_data["name"],
            "short": short,
            "normal": normal,
        })
    
    return leaderboard


def gen_leaderboard(leaderboard):
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

