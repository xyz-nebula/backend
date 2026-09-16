from os import getenv
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

VALKEY_HOST = getenv("VALKEY_HOST", "localhost")
VALKEY_PORT = int(getenv("VALKEY_PORT", "6379"))
VALKEY_DB = int(getenv("VALKEY_DB", "0"))