import requests
from utils.references import References

base_url = "https://discord.com/api/v8"

application_id = 945718535815049246
guild_id = 912435770290229348

headers = {
    "Authorization": f"Bot {References.BOT_TOKEN}"
}

print(headers)

print(base_url + f"/applications/{application_id}/guilds/{guild_id}/commands")

r = requests.put(base_url + f"/applications/{application_id}/guilds/{guild_id}/commands", headers=headers, json=[])
print(r.json())
print(r)
r = requests.put(base_url + f"/applications/{application_id}/commands", headers=headers, json=[])
print(r.json())
print(r)