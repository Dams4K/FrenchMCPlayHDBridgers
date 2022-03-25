import json
import os
import discord
import time
import requests
import inspect
from utils.lang.lang import Lang
from utils.references import References
from utils.bot_errors import *
from utils.bot_logging import get_logging

logging_error = get_logging(__name__, "error")
logging_info = get_logging(__name__, "info")
logging_debug = get_logging(__name__, "debug")

class APIS_URLS:
    MCPLAYHD_API_STATUS_URL = "https://mcplayhd.net/api/?token={token}"
    MCPLAYHD_API_URL = "https://mcplayhd.net/api/fastbuilder/{mode}/stats/{player}?token={token}"
    NAME_TO_UUID_URL = "https://api.mojang.com/users/profiles/minecraft/{player_name}"
    UUID_TO_NAME_URL = "https://api.mojang.com/user/profiles/{uuid}/names"


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
            self.data[player.uuid] = member.id
            logging_debug.debug(f"add player {member.id} in guild {self.parent.id}")
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
            response_args["embed"] = gen_error(Lang.get_text("PLAYER_UNFOUND", "fr", **kwargs))
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
    def update_player(self, uuid):
        player = Player(uuid=uuid)
        last_update = player.last_update
        
        player.last_update = int(time.time())
        last_scores = player.scores.copy()
        new_scores = player.update_scores()
        self.data[uuid] = player.to_dict()
        
        if last_scores == player.scores: return False # Nothing Change

        return new_scores

    @BaseData.manage_data
    def add_player(self, player):
        self.data[player.uuid] = player.to_dict()


class Player:
    def __init__(self, **options):
        self.uuid = options.get("uuid", None)
        self.name = options.get("name", None)
        assert self.name != None or self.uuid != None, "no uuid and no name set"

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
                "onestack": -1
            }

            KnownPlayers.add_player(self)
            

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
        # inclined = self.get_score("inclined")
        # onestack = self.get_score("onestack")

        inclined = self.scores["inclined"]
        onestack = self.scores["onestack"]
        last_scores = self.scores.copy()

        self.scores = {
            "normal": normal,
            "short": short,
            "inclined": inclined,
            "onestack": onestack
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
        if "error" in mojang_data.json():
            raise PlayerNotFound

        return mojang_data.json()["id"]


    def uuid_to_name(self):
        mojang_data = requests.get(APIS_URLS.UUID_TO_NAME_URL.format(uuid=self.uuid))
        if "error" in mojang_data.json():
            raise PlayerNotFound
            
        return mojang_data.json()[-1]["name"]


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