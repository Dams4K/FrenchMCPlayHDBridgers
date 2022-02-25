import csv

class _Lang:
    def __init__(self, file_path="utils/lang/lang.csv") -> None:
        self.file_path = file_path

        with open(self.file_path, newline='') as f:
            self.rows = [row for row in csv.reader(f, delimiter=",", quotechar='"')]


    def get_text(self, text_key: str, lang: str, **options) -> str:
        key_row: int = [row for row in range(len(self.rows)) if self.rows[row][0].upper() == text_key.upper()][0]
        lang_col: int = [col for col in range(len(self.rows[0])) if self.rows[0][col].lower() == lang.lower()][0]
        text: str = self.rows[key_row][lang_col]

        return text.format(**options)


Lang: _Lang = _Lang()