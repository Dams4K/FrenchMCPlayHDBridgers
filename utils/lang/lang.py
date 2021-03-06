import csv
import string
from utils.emojis import emojis_dict

class FormatDict(dict):
    def __missing__(self, key):
        return "{" + key + "}"

class _Lang:
    def __init__(self, file_path="utils/lang/lang.csv", emojis_dict={}) -> None:
        self.file_path = file_path
        self.emojis_dict = emojis_dict

        with open(self.file_path, newline='') as f:
            self.rows = [row for row in csv.reader(f, delimiter=",", quotechar='"')]


    def get_text(self, text_key: str, lang: str, **options) -> str:
        try:
            key_row: int = [row for row in range(len(self.rows)) if self.rows[row][0].upper() == text_key.upper()][0]
            lang_col: int = [col for col in range(len(self.rows[0])) if self.rows[0][col].lower() == lang.lower()][0]
            text: str = self.rows[key_row][lang_col]
            
            formatter = string.Formatter()
            mapping = FormatDict(**options, **self.emojis_dict)

            return formatter.vformat(text, (), mapping)
        except:
            return "message not found"


Lang: _Lang = _Lang(emojis_dict=emojis_dict)

if __name__ == "__main__":
    print(Lang.get_text("PLAYER_REMOVED_FROM_WHITELIST", "fr"))
    print(Lang.get_text("PLAYER_REMOVED_FROM_WHITELIST", "en"))
    print(Lang.get_text("qd", "en"))