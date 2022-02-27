import json
import os
import discord
import time
import requests
from utils.lang.lang import Lang
from utils.references import References

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
        return self.data

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
            "whitelist": []
        }
        super().__init__("datas/guilds/" + str(self.id) + ".json")
        self.whitelist = WhitelistData(self, self.data["whitelist"])
    

    def get_data(self):
        data = {
            "lang": "en",
            "whitelist": self.whitelist.data
        }
        return data


class WhitelistData:
    def __init__(self, parent: GuildData, data):
        self.parent = parent
        self.data = data
    

    def get_player(self, **kwargs):
        name = kwargs.get("name", None)
        uuid = kwargs.get("uuid", None)

        if name == uuid == None: return #TODO: catch error

        player = Player(name=name, uuid=uuid)

        return player



    @BaseData.manage_data
    def add_player(self, **kwargs):
        player = self.get_player(**kwargs)
        if player == None: return
        
        if player.uuid in self.data:
            return #TODO: catch player already in whitelist
        else:
            self.data.append(player.uuid)
    

    @BaseData.manage_data
    def remove_player(self, **kwargs):
        player = self.get_player(**kwargs)
        if player == None: return

        if not player.uuid in self.data:
            return #TODO: catch player already in whitelist
        else:
            self.data.remove(player.uuid)
    

    def player_list(self):
        print(len(self.data))
        msg = "```\n- " + "\n- ".join([Player(uuid=uuid).name for uuid in self.data]) + "\n```"
        return msg



class KnownPlayers(BaseData):
    def __init__(self):
        super().__init__(file_path="datas/known_player.json", base_data=[])
    

    def get_player(self, **kwargs):
        uuid = kwargs.get("uuid", None)
        name = kwargs.get("name", None)
        for player_data in self.data:
            if uuid == player_data["uuid"] or name == player_data["name"]:
                return player_data
        return False
    

    @BaseData.manage_data
    def add_player(self, player):
        player_data = {
            "uuid": player.uuid,
            "name": player.name,
            "scores": {},
            "last_update": int(time.time())
        }
        
        self.data.append(player_data)


class Player:
    def __init__(self, **options):
        self.uuid = options.get("uuid", None)
        self.name = options.get("name", None)
        self.known_players = KnownPlayers()
        assert self.name != None or self.uuid != None, "no uuid and no name set"

        player_data = self.known_players.get_player(name=self.name, uuid=self.uuid)
        
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
                
            self.known_players.add_player(self)
            

    def get_score(self, mode="normal"):
        assert self.can_request(1), "rate limit achieve"

        url = APIS_URLS.MCPLAYHD_API_URL.format(mode=mode, player=self.uuid, token=References.MCPLAYHD_API_TOKEN)

        mcplayhd_data = requests.get(url)
        stats = mcplayhd_data.json()["data"]["stats"]
        
        return stats["timeBest"]


    def can_request(self, cost):
        result = requests.get(APIS_URLS.MCPLAYHD_API_STATUS_URL.format(token=References.MCPLAYHD_API_TOKEN))
        result_data = result.json()["data"]["user"]
        
        if result_data["rateLimit"]-result_data["currentRate"] >= cost:
            return True
        return False
    

    def name_to_uuid(self):
        mojang_data = requests.get(APIS_URLS.NAME_TO_UUID_URL.format(player_name=self.name))
        assert not "error" in mojang_data.json(), "player does not exist"
        return mojang_data.json()["id"]


    def uuid_to_name(self):
        mojang_data = requests.get(APIS_URLS.UUID_TO_NAME_URL.format(uuid=self.uuid))   
        assert not "error" in mojang_data.json(), "player does not exist"
        return mojang_data.json()[-1]["name"]


# Data = _Data("datas/data.json")