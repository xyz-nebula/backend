import logging

from pydantic import BaseModel

from app.config.storage import StorageConfig, ValkeyConfig
from app.config.storage_type import StorageTypes
from app.repository.base import BaseRepository

logger = logging.getLogger(__name__)


class RepositoryFactory:
    """
    Factory class to create repository instances based on the storage type.

    This factory is responsible for creating instances of different repository
    implementations depending on the storage type specified in the configuration.
    Supported storage types include Redis and in-memory storage.

    Methods:
        create(config: StorageConfig) -> BaseRepository:
            Creates a repository instance based on the provided storage configuration.

        _create_local_repository(config: StorageConfig) -> BaseRepository:
            Creates an instance of LocalRepository for in-memory storage.

        _create_redis_repository(config: StorageConfig) -> BaseRepository:
            Creates an instance of RedisRepository for Redis-based storage.
    """

    @staticmethod
    def create(config: StorageConfig | ValkeyConfig | BaseModel) -> BaseRepository:
        """
        Create a repository instance based on the provided storage configuration.

        Args:
            config (Union[StorageConfig, BaseModel]): The configuration object specifying
                the storage type.

        Returns:
            BaseRepository: An instance of a repository based on the specified storage type.

        Raises:
            ValueError: If the storage type specified in the config is unknown.

        Examples:
            >>> config = StorageConfig(storage_type=StorageTypes.MEMORY)
            >>> repository = RepositoryFactory.create(config)
            >>> isinstance(repository, LocalRepository)
            True

            >>> config = StorageConfig(storage_type=StorageTypes.REDIS)
            >>> repository = RepositoryFactory.create(config)
            >>> isinstance(repository, RedisRepository)
            True

            >>> config = StorageConfig(storage_type="UNKNOWN_TYPE")
            >>> repository = RepositoryFactory.create(config)
            ValueError: Unknown storage type: UNKNOWN_TYPE, available types: ['redis', 'memory']
        """
        storage_type = config.model_dump().get("storage_type", StorageTypes.MEMORY)
        if storage_type == StorageTypes.VALKEY:
            valkey_config = ValkeyConfig(**config.model_dump(exclude={"storage_type"}))
            logger.info("Creating Valkey repository")
            return RepositoryFactory._create_valkey_repository(valkey_config)
        elif storage_type == StorageTypes.MEMORY:
            in_memory_config = StorageConfig(**config.model_dump(exclude={"storage_type"}))
            logger.info("Creating in-memory repository")
            return RepositoryFactory._create_local_repository(in_memory_config)
        else:
            logger.error("Unknown storage type: %s", storage_type)
            raise ValueError(
                f"Unknown storage type: {storage_type}, available types: {StorageTypes.values()}"
            )

    @staticmethod
    def _create_local_repository(config: StorageConfig) -> BaseRepository:
        """
        Create an instance of LocalRepository for in-memory storage.

        Args:
            config (StorageConfig): The configuration object specifying the storage type.

        Returns:
            BaseRepository: An instance of LocalRepository.
        """
        from app.repository.local import LocalRepository

        return LocalRepository(config)

    @staticmethod
    def _create_valkey_repository(
        config: ValkeyConfig,
    ) -> BaseRepository:
        """
        Create an instance of ValkeyRepository for Valkey-based storage.

        Args:
            config (ValkeyConfig): The configuration object specifying the storage type.

        Returns:
            BaseRepository: An instance of ValkeyRepository.
        """
        from .valkey import ValkeyRepository

        return ValkeyRepository(config)


def get_token_repository() -> BaseRepository:
    return RepositoryFactory.create(ValkeyConfig())


__all__ = ["RepositoryFactory", "get_token_repository"]
