from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.config.storage_type import StorageTypes
from app.config.config import settings

class StorageConfig(BaseModel):
    """
    Base configuration class for storage settings.

    This class serves as the base configuration for different storage types. It includes
    common configurations that can be shared across different storage backends. By default,
    the storage type is set to in-memory (`MEMORY`), which is suitable for simple or local
    development use cases.

    Attributes:
        storage_type (StorageTypes): The type of storage to use. Defaults to `StorageTypes.MEMORY`.
    """

    storage_type: StorageTypes = Field(default=StorageTypes.MEMORY)

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        populate_by_name=True,
        extra="allow",
        arbitrary_types_allowed=True,
    )


class ValkeyConfig(StorageConfig):
    """
    Configuration class for Valkey storage settings.

    This class extends `StorageConfig` to provide configuration specific to Valkey storage.
    It allows for setting up connection details such as host, port, database, and password.
    Additionally, it includes a method to construct the Valkey URL based on the provided configuration.

    Attributes:
        storage_type (StorageTypes): The type of storage to use. Defaults to `StorageTypes.valkey`.
        host (str): The hostname of the Valkey server. Defaults to "localhost".
        port (int): The port number on which the Valkey server is listening. Defaults to 6379.
        db (int): The Valkey database index to use. Defaults to 0.
        password (Optional[str]): The password for the Valkey server, if any. Defaults to None.
        url (Optional[str]): A custom Valkey URL, if provided. Defaults to None.
    """

    storage_type: StorageTypes = Field(default=StorageTypes.valkey)
    host: str = Field(default_factory=settings.valkey_host)
    port: int = Field(default_factory=settings.valkey_port)
    db: int = Field(default_factory=settings.valkey_db)
    # password: Optional[str] = Field(default_factory=lambda: config("valkey_PASSWORD", default=None))
    url: Optional[str] = Field(default=None)

    def __repr__(self) -> str:
        """
        Return a string representation of the Valkey configuration object.

        The representation includes all configuration attributes except the `url`,
        which is dynamically generated based on other attributes using the `get_url` method.

        Returns:
            str: The representation of the Valkey configuration.

        Examples:
            >>> config = ValkeyConfig(host="valkey-server", port=6380, db=1)
            >>> repr(config)
            'ValkeyConfig(storage_type=valkey, host=valkey-server, port=6380, db=1, url=valkey://valkey-server:6380/1)'
        """
        attributes = self.model_dump(exclude={"url"}, exclude_none=True)
        attributes["url"] = self.get_url()
        attributes["storage_type"] = self.storage_type.value
        attributes_str = ", ".join([f"{k}={v}" for k, v in attributes.items()])
        return f"ValkeyConfig({attributes_str})"

    def __str__(self) -> str:
        """
        Return a string representation of the Valkey configuration object.

        This method calls `__repr__` to provide a consistent string representation.

        Returns:
            str: The representation of the Valkey configuration.

        Examples:
            >>> config = ValkeyConfig(host="valkey-server", port=6380, db=1)
            >>> str(config)
            'ValkeyConfig(storage_type=valkey, host=redis-server, port=6380, db=1, url=redis://redis-server:6380/1)'
        """
        return self.__repr__()

    def get_url(self) -> str:
        """
        Construct the Valkey URL based on the configuration attributes.

        If a custom `url` is provided, it is returned as is. Otherwise, a URL is
        constructed using the `host`, `port`, `db`, and optionally `password` attributes.

        Returns:
            str: The constructed Valkey URL.

        Examples:
            >>> config = ValkeyConfig(host="valkey-server", port=6380, db=1, password="secret")
            >>> config.get_url()
            'valkey://:secret@redis-server:6380/1'

            >>> config_no_pass = ValkeyConfig(host="valkey-server", port=6380, db=1)
            >>> config_no_pass.get_url()
            'valkey://redis-server:6380/1'
        """
        if self.url:
            return self.url
        if self.password:
            return f"valkey://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"valkey://{self.host}:{self.port}/{self.db}"


__all__ = ["StorageConfig", "ValkeyConfig"]