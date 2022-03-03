import json
import os
import discord
import time
import requests
import inspect
from utils.lang.lang import Lang
from utils.references import References
from utils.bot_errors import *

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
                self.data = json.load(f)
        else:
            self.save_data()


    def save_data(self):
        with open(self.file_path, "w") as f:
            data = self.get_data()
            if data != None:
                json.dump(data, f, indent=4)
    

    def get_data(self):
        return self.data.copy()

    def manage_data(func):
        def decorator(self, *args, **kwargs):
            parent = getattr(self, "parent", self)
            if parent == None and not hasattr(self, "save_data"): return #TODO: catch error
            
            result = func(self, *args, **kwargs)
            
            parent.save_data()

            return result
        return decorator


class GuildData(BaseData):
    def __init__(self, id):
        self.id = id
        self.data = {
            "lang": "en",
            "whitelist": {}
        }
        self.whitelist = WhitelistData(self, {})
        super().__init__("datas/guilds/" + str(self.id) + ".json")
        self.whitelist = WhitelistData(self, self.data["whitelist"])
    

    def get_data(self):
        data = {
            "lang": "fr",
            "whitelist": self.whitelist.data
        }
        return data.copy()


class WhitelistData:
    def __init__(self, parent: GuildData, data):
        self.parent = parent
        self.data = data
    

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

        player = self.get_player(**kwargs)
        if player == None: return Lang.get_text("PLAYER_UNFOUND", "fr", **kwargs)
        
        if player.uuid in self.data:
            return Lang.get_text("PLAYER_ALDREADY_IN_WHITELIST", "fr", **kwargs)
        else:
            self.data[player.uuid] = member.id
            return Lang.get_text("PLAYER_ADDED_ON_WHITELIST", "fr", **kwargs)
    

    @BaseData.manage_data
    def remove_player(self, **kwargs):
        player = self.get_player(**kwargs)
        if player == None: return

        if not player.uuid in self.data:
            return #TODO: catch player already in whitelist
        else:
            self.data.pop(player.uuid)
    

    def player_list(self):
        print(len(self.data))
        msg = "```\n- " + "\n- ".join([Player(uuid=uuid).name for uuid in self.data]) + "\n```"
        return msg



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
    def add_player(self, player):
        player_data = {
            "uuid": player.uuid,
            "name": player.name,
            "scores": {
                "normal": 0,
                "short": 0,
                "inclined": 0,
                "onestack": 0
            },
            "last_update": int(time.time())
        }
        
        self.data[player.uuid] = player_data


class Player:
    def __init__(self, **options):
        self.uuid = options.get("uuid", None)
        self.name = options.get("name", None)
        assert self.name != None or self.uuid != None, "no uuid and no name set"

        player_data = KnownPlayers.get_player(name=self.name, uuid=self.uuid)
        
        if player_data:
            self.uuid = player_data["uuid"]
            self.name = player_data["name"]
        else:

            if self.name != None:
                self.uuid = self.name_to_uuid()
            else:
                self.name = self.uuid_to_name()

            if not "-" in self.uuid:
                self.uuid = self.uuid[:8] + "-" + self.uuid[8:12] + "-" + self.uuid[12:16] + "-" + self.uuid[16:20] + "-" + self.uuid[20:]
                
            KnownPlayers.add_player(self)
            

    def get_score(self, mode="normal"):
        if not self.can_request(1):
            return {"error": "rate limit reached"}

        url = APIS_URLS.MCPLAYHD_API_URL.format(mode=mode, player=self.uuid, token=References.MCPLAYHD_API_TOKEN)

        mcplayhd_data = requests.get(url)
        if not "stats" in mcplayhd_data.json()["data"]:
            return None
        stats = mcplayhd_data.json()["data"]["stats"]
        if stats == None:
            print(f"stats is None for {self.uuid} : {self.name} in {mode}")
            return None
        else:
            return stats["timeBest"]


    def get_all_scores(self):
        normal = self.get_score("normal")
        short = self.get_score("short")
        inclined = self.get_score("inclined")
        onestack = self.get_score("onestack")

        all_scores = {
            "normal": normal if isinstance(normal, int) else "undefined",
            "short": short if isinstance(short, int) else "undefined",
            "inclined": inclined if isinstance(inclined, int) else "undefined",
            "onestack": onestack if isinstance(onestack, int) else "undefined"
        }
        return all_scores


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

KnownPlayers = _KnownPlayers()
# Data = _Data("datas/data.json")