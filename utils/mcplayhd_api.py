import requests
from utils.references import References

MCPLAYHD_API_STATUS_URL = "https://mcplayhd.net/api/?token={token}"
MCPLAYHD_API_URL = "https://mcplayhd.net/api/fastbuilder/{mode}/stats/{player}?token={token}"
NAME_TO_UUID_URL = "https://api.mojang.com/users/profiles/minecraft/{player_name}"
UUID_TO_NAME_URL = "https://api.mojang.com/user/profiles/{uuid}/names"

class Player:
    def __init__(self, **options):
        self.uuid = options.get("uuid", None)
        self.name = options.get("name", None)

        assert self.name != None or self.uuid != None, "no uuid and no name set"

        if self.name != None:
            self.uuid = self.name_to_uuid()
        else:
            self.name = self.uuid_to_name()

        if not "-" in self.uuid:
            self.uuid = self.uuid[:8] + "-" + self.uuid[8:12] + "-" + self.uuid[12:16] + "-" + self.uuid[16:20] + "-" + self.uuid[20:]

    def get_score(self, mode="normal"):
        assert self.can_request(1), "rate limit achieve"

        url = MCPLAYHD_API_URL.format(mode=mode, player=self.uuid, token=References.MCPLAYHD_API_TOKEN)

        mcplayhd_data = requests.get(url)
        stats = mcplayhd_data.json()["data"]["stats"]
        
        return stats["timeBest"]


    def can_request(self, cost):
        result = requests.get(MCPLAYHD_API_STATUS_URL.format(token=References.MCPLAYHD_API_TOKEN))
        result_data = result.json()["data"]["user"]
        
        if result_data["rateLimit"]-result_data["currentRate"] >= cost:
            return True
        return False
    

    def name_to_uuid(self):
        mojang_data = requests.get(NAME_TO_UUID_URL.format(player_name=self.name))
        assert "id" in mojang_data.json(), "player does not exist"
        return mojang_data.json()["id"]


    def uuid_to_name(self):
        mojang_data = requests.get(UUID_TO_NAME_URL.format(uuid=self.uuid))
        assert not "error" in mojang_data.json(), "player does not exist"
        return mojang_data.json()[-1]["name"]

if __name__ == "__main__":
    player = Player("Dams4K")
    print( format(player.get_score("short")/1000, ".3f")  )