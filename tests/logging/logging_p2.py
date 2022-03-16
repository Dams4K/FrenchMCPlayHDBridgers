import logging

logger = logging.getLogger(__name__)

formatter = logging.Formatter("%(levelname)s:%(name)s:%(asctime)s:%(filename)s:%(funcName)s -> %(message)s")

file_handler = logging.FileHandler("tests/logging/logging.log")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)

def cube(x):
    result = x**3
    logger.debug(f"x: {x}; return value: {result}")
    return result

cube(5)