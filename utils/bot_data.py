import json
import os
import discord
import time
import requests
import inspect
from utils.lang.lang import Lang
from utils.references import References
from cogs.errors import *
from utils.bot_logging import get_logging

logging_error = get_logging(__name__, "error")
logging_info = get_logging(__name__, "info")
logging_debug = get_logging(__name__, "debug")

class APIS_URLS:
    MCPLAYHD_API_STATUS_URL = "https://mcplayhd.net/api/?token={token}"
    MCPLAYHD_API_URL = "https://mcplayhd.net/api/fastbuilder/{mode}/stats/{player}?token={token}"
    NAME_TO_UUID_URL = "https://api.mojang.com/users/profiles/minecraft/{player_name}"
    UUID_TO_NAME_URL = "https://api.mojang.com/user/profiles/{uuid}/names"
    PROFILE_URL = "https://sessionserver.mojang.com/session/minecraft/profile/{uuid}"


class BaseData:
    def __init__(self, file_path, base_data = {}):
        self.file_path = file_path
        self.data = base_data if not hasattr(self, "data") else self.data
        self.load_data()


    def load_data(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                # logging_info.info(f"load data from {self}")
                self.data = json.load(f)
        else:
            self.save_data()


    def save_data(self):
        data = self.get_data()
        if data != None:
            with open(self.file_path, "w") as f:
                # logging_info.info(f"save data from {self}")
                json.dump(data, f, indent=4)
    

    def get_data(self):
        return self.data.copy()

    def manage_data(func):
        def decorator(self, *args, **kwargs):
            parent = getattr(self, "parent", self)
            if parent == None and not hasattr(parent, "save_data") and not hasattr(parent, "load_data"): assert False, f"{self} <-> manage_data -> decorator -> not save or load func in parent"
            parent.load_data()
            
            result = func(self, *args, **kwargs)
            
            parent.save_data()

            return result
        return decorator


class GuildData(BaseData):
    def __init__(self, id):
        self.id = id
        self.whitelist = None
        self.data = {
            "lang": "fr",
            "whitelist": {},
            "pb_channel": None,
            "spreadsheet_id": None
        }

        super().__init__("datas/guilds/" + str(self.id) + ".json")
        self.whitelist = WhitelistData(self, self.data["whitelist"])
        self.sheet: LeaderboardSheet = LeaderboardSheet(self)
    

    def get_data(self):
        data = self.data.copy()
        whitelist_data = getattr(self.whitelist, "data", {}).copy()
        data["whitelist"] = whitelist_data
        return data

    def get_pb_channel(self):
        return self.data.get("pb_channel", None)
    
    def get_spreadsheet_id(self):
        return self.data.get("spreadsheet_id", None)


    @BaseData.manage_data
    def set_pb_channel(self, new_id):
        self.data["pb_channel"] = new_id
    
    @BaseData.manage_data
    def set_spreadsheet_id(self, new_id):
        self.data["spreadsheet_id"] = new_id


class WhitelistData:
    def __init__(self, parent: GuildData, data):
        self.parent = parent
        self.data = data
    

    def get_data(self):
        return self.data.copy()


    def get_player(self, **kwargs):
        name = kwargs.get("name", None)
        uuid = kwargs.get("uuid", None)

        if name == uuid == None: return #TODO: catch error

        try:
            player = Player(name=name, uuid=uuid)
            return player
        except PlayerNotFound:
            return None



    @BaseData.manage_data
    def add_player(self, **kwargs):
        print(kwargs.get("name"))
        member = kwargs.pop("member")
        response_args = {
            "content": "nothing to say..."
        }

        player = self.get_player(**kwargs)
        
        if player == None:
            response_args["content"] = ""
            response_args["embed"] = gen_error(Lang.get_text("PLAYER_UNFOUND", "fr", **kwargs))
        elif player.uuid in self.data:
            response_args["content"] = Lang.get_text("PLAYER_ALDREADY_IN_WHITELIST", "fr", **kwargs)
        else:
            self.data[player.uuid] = member.id if member else None
            logging_debug.debug(f"add player {member.id if member else None} in guild {self.parent.id}")
            response_args["content"] = Lang.get_text("PLAYER_ADDED_ON_WHITELIST", "fr", **kwargs)
        
        return response_args
    

    @BaseData.manage_data
    def remove_player(self, **kwargs):
        player = self.get_player(**kwargs)
        
        response_args = {
            "content": "nothing to say..."
        }

        if player == None:
            response_args["content"] = ""
            response_args["embed"] = gen_error(Lang.get_text("PLAYER_UNFOUND", "fr", **kwargs)) #TODO: changer ça, les erreurs doivent etre géré dans la cog errors
        elif not player.uuid in self.data:
            response_args["content"] = Lang.get_text("PLAYER_NOT_IN_WHITELIST", "fr", **kwargs)
        else:
            self.data.pop(player.uuid)
            response_args["content"] = Lang.get_text("PLAYER_REMOVED_FROM_WHITELIST", "fr", **kwargs)

        return response_args


class _KnownPlayers(BaseData):
    def __init__(self):
        super().__init__(file_path="datas/known_player.json", base_data=[])
    

    def get_player(self, **kwargs):
        uuid = kwargs.get("uuid", None)
        name = kwargs.get("name", None)

        if uuid:
            return self.data.get(uuid)
        else:
            for i in self.data:
                player_data = self.data[i]
                if name.lower() == player_data["name"].lower():
                    return player_data
        
        return False
    

    @BaseData.manage_data
    def update_player(self, player):
        assert isinstance(player, Player), f"{player} not from player class"

        last_update = player.last_update
        
        player.name = player.uuid_to_name()
        player.last_update = int(time.time())
        last_scores = player.scores.copy()
        new_scores = player.update_scores()
        self.data[player.uuid] = player.to_dict()
        
        if last_scores == player.scores: return False # Nothing Change

        return new_scores

    @BaseData.manage_data
    def add_player(self, player):
        self.data[player.uuid] = player.to_dict()


class Player:
    def __init__(self, **options):
        self.uuid = options.get("uuid", None)
        self.name = options.get("name", None)
        self.faked = options.get("faked", False)

        assert self.name != None or self.uuid != None or self.faked, "no uuid and no name set"

        if not self.faked:
            player_data = KnownPlayers.get_player(name=self.name, uuid=self.uuid)
        
            if player_data:
                self.uuid = player_data["uuid"]
                self.name = player_data["name"]
                self.scores = player_data["scores"]
                self.last_update = player_data["last_update"]
            else:
                if self.name != None:
                    self.uuid = self.name_to_uuid()
                else:
                    self.name = self.uuid_to_name()

                self.uuid = self.uuid.replace("-", "")
                self.uuid = self.uuid[:8] + "-" + self.uuid[8:12] + "-" + self.uuid[12:16] + "-" + self.uuid[16:20] + "-" + self.uuid[20:]
                self.last_update = 0
                self.scores = {
                    "normal": -1,
                    "short": -1,
                    "inclined": -1,
                    "onestack": -1,
                    "inclinedshort": -1
                }
                KnownPlayers.add_player(self)
        else:
            self.last_update = 0
            self.scores = {
                "normal": -1,
                "short": -1,
                "inclined": -1,
                "onestack": -1,
                "inclinedshort": -1
            }

    @property
    def short(self): return self.scores["short"] if self.scores["short"] != None else -1
    @property
    def normal(self): return self.scores["normal"] if self.scores["normal"] != None else -1
    @property
    def inclined(self): return self.scores["inclined"] if self.scores["inclined"] != None else -1
    @property
    def onestack(self): return self.scores["onestack"] if self.scores["onestack"] != None else -1
    @property
    def inclinedshort(self):
        self.scores.setdefault("inclinedshort", -1)
        return self.scores["inclinedshort"] if self.scores["inclinedshort"] != None else -1
    @property
    def global_score(self): return int(round(self.normal / 2 + self.short, 3))


    def get_score(self, mode="normal"):
        if not self.can_request(1):
            return -1

        url = APIS_URLS.MCPLAYHD_API_URL.format(mode=mode, player=self.uuid, token=References.MCPLAYHD_API_TOKEN)

        mcplayhd_data = requests.get(url)
        if not "stats" in mcplayhd_data.json()["data"]:
            return None
        stats = mcplayhd_data.json()["data"]["stats"]
        if stats == None:
            logging_debug.debug(f"stats is None for {self.uuid} : {self.name} in {mode}")
            return None
        else:
            return stats["timeBest"]


    def update_scores(self):
        """Return dict of best times of all different modes
        of the player
        -1 when the player haven't personal best yet
        """
        normal = self.get_score("normal")
        short = self.get_score("short")
        inclined = self.get_score("inclined")
        onestack = self.get_score("onestack")
        inclinedshort = self.get_score("inclinedshort")

        last_scores = self.scores.copy()

        self.scores = {
            "normal": normal,
            "short": short,
            "inclined": inclined,
            "onestack": onestack,
            "inclinedshort": inclinedshort
        }

        new_scores = {k: v for k, v in self.scores.items() if (k, v) not in last_scores.items()}
        return new_scores


    def can_request(self, cost):
        result = requests.get(APIS_URLS.MCPLAYHD_API_STATUS_URL.format(token=References.MCPLAYHD_API_TOKEN))
        result_data = result.json()["data"]["user"]
        
        if result_data["rateLimit"]-result_data["currentRate"] >= cost:
            return True
        return False
    

    def name_to_uuid(self):
        mojang_data = requests.get(APIS_URLS.NAME_TO_UUID_URL.format(player_name=self.name))
        if mojang_data.text.replace(" ", "") == "" or "error" in mojang_data.json():
            raise PlayerNotFound

        return mojang_data.json()["id"]


    def uuid_to_name(self):
        mojang_data = requests.get(APIS_URLS.PROFILE_URL.format(uuid=self.uuid))
        if "errorMessage" in mojang_data.json() or not "name" in mojang_data:
            print(mojang_data)
            # raise PlayerNotFound
            return None
            
        return mojang_data.json()["name"]


    def to_dict(self):
        return {
            "uuid": self.uuid,
            "name": self.name,
            "scores": self.scores.copy(),
            "last_update": self.last_update
        }

KnownPlayers = _KnownPlayers()

def get_current_status():
    return requests.get(APIS_URLS.MCPLAYHD_API_STATUS_URL.format(token=References.MCPLAYHD_API_TOKEN)).json()


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


class LeaderboardSheet:
    GLOBAL_SHEET = "Global (Bot)!A1:F"
    NORMAL_SHEET = "Normal!A1:D"
    SHORT_SHEET = "Short!A1:D"
    INCLINED_SHEET = "Inclined!A1:D"
    ONESTACK_SHEET = "Onestack!A1:D"
    INCLINEDSHORT_SHEET = "InclinedShort!A1:D"

    SHEETS = [
        GLOBAL_SHEET,
        NORMAL_SHEET,
        SHORT_SHEET,
        INCLINED_SHEET,
        ONESTACK_SHEET,
        INCLINEDSHORT_SHEET
    ]

    SHORT_SUB_TIME = 6000
    NORMAL_SUB_TIME = 12000
    ONESTACK_SUB_TIME = 12050
    INCLINED_SUB_TIME = 9000
    INCLINEDSHORT_SUB_TIME = 9000

    def __init__(self, parent: GuildData):
        self.parent: GuildData = parent

        self.credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        self.service = build('sheets', 'v4', credentials=self.credentials)
        self.sheet = self.service.spreadsheets()

        self.spreadsheet_id = parent.get_spreadsheet_id()


    def calc_global_score(self, short: int, normal: int):
        return round(int(normal) / 2 + int(short), 3)


    def update_player(self, player: Player, sheet):
        last_pos = self.get_player_pos(player, self.parse_sheet(sheet))
        n_lb = self.gen_leaderboard(sheet)
        new_pos = self.get_player_pos(player, n_lb)

        if (
            (sheet in [self.GLOBAL_SHEET, self.SHORT_SHEET] and -1 <  player.short < self.SHORT_SUB_TIME) or
            (sheet == self.NORMAL_SHEET and -1 < player.normal < self.NORMAL_SUB_TIME) or
            (sheet == self.INCLINED_SHEET and -1 < player.inclined < self.INCLINED_SUB_TIME) or
            (sheet == self.ONESTACK_SHEET and -1 < player.onestack < self.ONESTACK_SUB_TIME) or
            (sheet == self.INCLINEDSHORT_SHEET and -1 < player.inclinedshort < self.INCLINEDSHORT_SUB_TIME)
        ):
            self.update_sheet(sheet, n_lb)
            return last_pos, new_pos
        return False, False


    def gen_leaderboard(self, sheet, players_overrider=[]):
        lb = {}
        template = ["name"]
        if sheet == LeaderboardSheet.GLOBAL_SHEET: template += ["normal", "short"]
        elif sheet == LeaderboardSheet.NORMAL_SHEET: template += ["normal"]
        elif sheet == LeaderboardSheet.SHORT_SHEET: template += ["short"]
        elif sheet == LeaderboardSheet.INCLINED_SHEET: template += ["inclined"]
        elif sheet == LeaderboardSheet.ONESTACK_SHEET: template += ["onestack"]
        elif sheet == LeaderboardSheet.INCLINEDSHORT_SHEET: template += ["inclinedshort"]

        w_uuids = self.parent.whitelist.get_data()
        for overrider_player in players_overrider:
            if overrider_player.uuid in w_uuids:
                w_uuids.pop(overrider_player.uuid)
        w_players = [Player(uuid=p_uuid) for p_uuid in w_uuids]
        w_players.extend(players_overrider)

        for player in w_players:
            if sheet == LeaderboardSheet.GLOBAL_SHEET: #TODO: faire ça autrement, on repete trop de fois cette condition qui est utile qu'une fois 
                if -1 not in [getattr(player, k) for k in template if k != "name"] and -1 < player.short < self.SHORT_SUB_TIME:
                    time = player.global_score
                    
                    lb.setdefault(time, [])

                    lb[time].append({k : (getattr(player, k) if k != "name" else player.name) for k in template})
        
            else:
                if -1 < getattr(player, template[-1]) < getattr(self, template[-1].upper() + "_SUB_TIME"):
                    time = getattr(player, template[-1])
                    
                    lb.setdefault(time, [])
                    lb[time].append({"name": player.name, template[-1]: time})

        return lb


    def get_player_pos(self, player: Player, lb: dict):
        if lb == None:
            return -1
        lb_times = list(lb.keys())
        lb_times.sort()

        i, pos, gap, find = 0, -1, 0, False

        while not find and i < len(lb_times):
            pos = i + gap
            for player_infos in lb[lb_times[i]]:
                if player_infos["name"] == player.name:
                    find = True

            gap += len(lb[lb_times[i]])-1     
            i+=1
        
        return pos+1 if find else -1



    def get_sheet_values(self, sheet):
        return self.sheet.values().get(spreadsheetId=self.spreadsheet_id, range=sheet).execute().get("values", [])


    def get_columns(self, values=None, sheet=None):
        assert values != None or sheet != None, "values and sheet are None"
        if values == None and sheet != None: values = self.get_sheet_values(sheet)
    
        # if values == []: return ["Classement", "Pseudo", "", "PBs"]

        return [e.lower().replace("pb", "").replace(" ", "").replace("pseudo", "name") for e in values.pop(0)]

    
    def update_sheet(self, sheet, n_lb):
        formatted_sheet = self.format_sheet(sheet, n_lb)
        
        try:
            self.sheet.values().clear(spreadsheetId=self.spreadsheet_id, range=sheet).execute()
            request = self.sheet.values().update(
                spreadsheetId=self.spreadsheet_id, range=sheet,
                valueInputOption="USER_ENTERED", body={"values": formatted_sheet}
            ).execute()
        except Exception as e:
            print("Error with the sheet", e)


    def format_sheet(self, sheet, n_lb):
        print("format sheet", sheet)
        times = list(n_lb.keys())
        if None in times: times.remove(None)
        times.sort()
        
        columns = self.get_columns(sheet=sheet)
        values = [e.replace("name", "pseudo") for e in columns[:]]
        values = [ [e[:1].upper() + e[1:] for e in values[:]] ]
        values.append([""]*len(values[0]))

        gap = 0
        for i in range(len(times)):
            pos = i+1+gap
            for player_data in n_lb[times[i]]:
                if sheet == LeaderboardSheet.INCLINEDSHORT_SHEET:
                    print(player_data)
                to_append = [
                    e.replace(
                        "classement", "#" + str(pos)
                    ).replace(
                        "name", str(player_data["name"])
                    ).replace(
                        "normal/2+short", format(times[i]/1000, ".3f")
                    ).replace(
                        "normal", format(player_data.get("normal", -1)/1000, ".3f")
                    ).replace(
                        "short", format(player_data.get("short", -1)/1000, ".3f")
                    ).replace(
                        "inclined", format(player_data.get("inclined", -1)/1000, ".3f")
                    ).replace(
                        "onestack", format(player_data.get("onestack", -1)/1000, ".3f")
                    ).replace(
                        "inclinedshort", format(player_data.get("inclinedshort", -1)/1000, ".3f")
                    )
                    for e in columns
                ]
                values.append(to_append)
            gap += len(n_lb[times[i]])-1

        return values


    def parse_sheet(self, sheet):
        try:
            values = self.get_sheet_values(sheet)
        except:
            return None

        leaderboard = {}
        if values != []:
            columns = self.get_columns(values=values)
            order = [e for e in columns if e in ["name", "short", "normal", "inclined", "onestack", "inclinedshort"]]

            for player_infos in values:
                if player_infos == []: continue

                d = {k : self.parse_str_to_nbr(player_infos[columns.index(k)]) if k != "name" else player_infos[columns.index(k)] for k in order}

                time = None
                if sheet == LeaderboardSheet.GLOBAL_SHEET:
                    time = self.calc_global_score(d["short"]*1000, d["normal"]*1000)
                else:
                    time = list(d.values())[-1]
                
                leaderboard.setdefault(time, [])
                leaderboard[time].append(d)
            
        return leaderboard

    def parse_str_to_nbr(self, s: str):
        if s.isdigit(): return int(s)
        if s.replace(".", "").isdigit() and s.count(".") <= 1: return float(s)
        else: return s

        return leaderboard


if __name__ == "__main__":
    p = Player(name="Dams4K")
    print(p.global_score)
    # KnownPlayers.update_player(p)
    # gd: GuildData = GuildData(892459726212837427)
    # print(gd.sheet.update_player(p, LeaderboardSheet.ONESTACK_SHEET))