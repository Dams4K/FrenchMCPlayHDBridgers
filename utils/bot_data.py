import json
import os
from utils.lang.lang import Lang
from utils.mcplayhd_api import Player
import time

class DataActions:
    ADD = 0
    REMOVE = 1
    LIST = 2

class _Data:
    def __init__(self, data_path):
        self.DATA_PATH = data_path
        self.data = {}
        self.load_data()
    
    def load_data(self):
        if os.path.exists(self.DATA_PATH):
            with open(self.DATA_PATH, "r") as f:
                self.data = json.load(f)
        else:
            self.save_data()


    def save_data(self):
        with open(self.DATA_PATH, "w") as f:
            json.dump(self.data, f, indent=4)
    
    def _create_guild_data(self, guild_id):
        if guild_id in self.data: return
        
        self.data[guild_id] = {
            "lang": "en",
            "whitelist": {}
        }

    def whitelist(self, action: DataActions, guild_id: str, player_name: str = ""):
        self._create_guild_data(guild_id)

        lang = self.data[guild_id]["lang"]
        whitelist_data: dict = self.data[guild_id]["whitelist"]

        if player_name != "": player = Player(name=player_name)

        err, message = False, "no_message"

        if action == DataActions.ADD:
            if not player.uuid in whitelist_data:
                whitelist_data[player.uuid] = {}
                err, message = False, Lang.get_text("PLAYER_ADDED_FROM_WHITELIST", lang, name=player_name)

            else:
                err, message = True, Lang.get_text("PLAYER_ALREADY_IN_WHITELIST", lang, name=player_name)

        elif action == DataActions.REMOVE:
            if player.uuid in whitelist_data:
                whitelist_data.pop(player.uuid)
                err, message = False, Lang.get_text("PLAYER_REMOVED_FROM_WHITELIST", lang, name=player_name)

            else:
                err, message = True, Lang.get_text("PLAYER_ALREADY_NOT_IN_WHITELIST", lang, name=player_name)
        
        elif action == DataActions.LIST:
            message = "```\n- " + "\n- ".join([Player(uuid=e).name for e in whitelist_data]) + "\n```"

        self.save_data()
        return err, message
    

    def set_lang(self, guild_id, lang_id: str):
        self._create_guild_data(guild_id)
        self.data[guild_id]["lang"] = lang_id


class BaseData:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None


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
            parent = getattr(self, "parent", None)
            if parent == None: return #TODO: catch error

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
        self.whitelist = None
        self.whitelist = WhitelistData(self, [])

        self.file_path = "datas/guilds/" + str(self.id) + ".json"
        self.load_data()
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



Data = _Data("datas/data.json")