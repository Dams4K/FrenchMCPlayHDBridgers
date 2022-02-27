import requests
from utils.references import References
import time


if __name__ == "__main__":
    player = Player("Dams4K")
    print( format(player.get_score("short")/1000, ".3f")  )