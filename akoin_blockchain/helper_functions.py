import logging
import os
import random
import string
import time

from dotenv import load_dotenv
from typing import Optional
from urllib.parse import urlparse

load_dotenv()


def days_ago(timestamp: float) -> int:
    return (time.time() - timestamp) / 60 / 60 / 24  # seconds to days


def generate_random_string(n: Optional[int]=64) -> str:
    all_chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join(random.SystemRandom().choice(all_chars) for _ in range(n))


def is_url_valid(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

    
def get_logger(name: str, level: Optional[int]=logging.DEBUG) -> logging.Logger:
    logger = logging.getLogger(name)
    if os.getenv('LOGGING_LEVEL'):
        level = int(os.getenv('LOGGING_LEVEL'))
    logger.setLevel(level)
    formatter = logging.Formatter("%(asctime)s : %(filename)s : %(funcName)s : %(lineno)d : %(levelname)s : %(message)s")
    
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger
