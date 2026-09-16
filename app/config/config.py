from os import getenv
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field


REDIS_HOST = getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(getenv("REDIS_PORT", "6379"))
REDIS_DB = int(getenv("REDIS_DB", "0"))