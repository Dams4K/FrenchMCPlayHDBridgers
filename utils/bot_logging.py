# I know it's not like this i should do, but i do want i want so :middle_finger: ahaaahhh, BAD DEV GO BRRRRRRRRRRRRRRRRRRRRRRRR
import logging, os, time

LOGGING_PATH = "datas/logs/logging.log"

def create_new_log():
    if os.path.exists(LOGGING_PATH):
        assert os.path.isfile(LOGGING_PATH), "path is a folder WHAT R U DOING"
    
        os.rename(LOGGING_PATH, LOGGING_PATH + " - " + time.ctime(os.path.getctime(LOGGING_PATH)))


def get_logging(name: str, level: str):
    assert level.upper() in logging._nameToLevel, "level didn't exist"

    logger = logging.getLogger(name)

    formatter = logging.Formatter("[%(levelname)s : %(filename)s] [%(asctime)s]:%(funcName)s -> %(message)s")

    file_handler = logging.FileHandler(LOGGING_PATH)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.setLevel(logging._nameToLevel[level.upper()])

    return logger