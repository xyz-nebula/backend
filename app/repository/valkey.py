from typing import Any, Optional

from valkey.asyncio import Redis

from app.config.storage import ValkeyConfig
from app.config.types import EXPIRATION_DTYPE
from app.repository.base import BaseRepository
from app.utils.time_helpers import cast_to_seconds


class ValkeyRepository(BaseRepository):
    """
    Repository implementation using valkey with asynchronous capabilities.

    This class provides an interface to interact with valkey as a key-value store.
    It allows storing, retrieving, and deleting values asynchronously, with support
    for optional expiration times.

    Attributes:
        _config (ValkeyConfig): Configuration object for connecting to Redis.
        _valkey (Redis): Redis client instance used for interacting with the Redis database.
    """

    def __init__(self, config: ValkeyConfig):
        """
        Initialize the ValkeyRepository with a given configuration.

        Args:
            config (ValkeyConfig): The configuration object containing Redis connection details.
        """
        self._config: ValkeyConfig = config
        self._valkey: Redis = Redis.from_url(self._config.get_url(), decode_responses=True)

    @property
    def valkey(self) -> Redis:
        """
        Get the valkey client instance.

        Returns:
            valkey: The Redis client instance used for interacting with the Redis database.
        """
        return self._valkey

    @property
    def config(self) -> ValkeyConfig:
        """
        Get the current configuration of the repository.

        Returns:
            ValkeyConfig: The configuration object for the repository.
        """
        return self._config

    async def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the valkey store by its key.

        Args:
            key (str): The key for the value to retrieve.

        Returns:
            Optional[Any]: The value associated with the key, or None if the key is not found.

        Examples:
            >>> config = ValkeyConfig(host="localhost", port=6379, db=0)
            >>> repo = ValkeyRepository(config)
            >>> await repo.set("sample_key", "sample_value")
            >>> value = await repo.get("sample_key")
            >>> print(value)
            'sample_value'
        """
        value = await self._valkey.get(key)
        # valkey-py can return either bytes or str depending on configuration.
        # we created the client with ``decode_responses=True`` so values are
        # already str; attempting to decode them leads to the ``'str' object
        # has no attribute 'decode'`` error seen during authentication.  If a
        # bytes value is returned for some reason, decode it, otherwise just
        # return whatever we got.
        if value is None:
            return None
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return value

    async def set(
        self,
        key: str,
        value: str,
        expiration: Optional[EXPIRATION_DTYPE] = None,
    ) -> None:
        """
        Store a value in the valkey store with an optional expiration time.

        Args:
            key (str): The key to associate with the value.
            value (str): The value to store.
            expiration (Optional[Union[int, float, datetime.timedelta]]): Optional expiration time
                for the key in seconds or as a timedelta. If not provided, the key will not expire.

        Returns:
            None

        Examples:
            >>> config = ValkeyConfig(host="localhost", port=6379, db=0)
            >>> repo = ValkeyRepository(config)
            >>> await repo.set("temp_key", "temp_value", expiration=60)
            # The value will expire after 60 seconds.
        """
        casted_expiration = cast_to_seconds(expiration)
        if casted_expiration:
            await self._valkey.set(key, value, ex=casted_expiration)
        else:
            await self._valkey.set(key, value)

    async def delete(self, key: str) -> None:
        """
        Delete a value from the valkey store by its key.

        Args:
            key (str): The key for the value to delete.

        Returns:
            None

        Examples:
            >>> config = valkeyConfig(host="localhost", port=6379, db=0)
            >>> repo = valkeyRepository(config)
            >>> await repo.set("delete_key", "delete_value")
            >>> await repo.delete("delete_key")
            >>> value = await repo.get("delete_key")
            >>> print(value)
            None  # The value has been deleted.
        """
        await self._valkey.delete(key)


__all__ = ["ValkeyRepository"]