import logging
import logging_p2

logger = logging.getLogger(__name__)

formatter = logging.Formatter("%(levelname)s:%(name)s:%(asctime)s:%(filename)s:%(funcName)s -> %(message)s")

file_handler = logging.FileHandler("tests/logging/logging.log")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

def square(x):
    result = x**2
    logger.info(f"x: {x}; return value: {result}")
    return result

square(5)