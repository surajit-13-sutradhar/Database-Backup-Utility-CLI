from abc import ABC, abstractmethod


class BaseStorage(ABC):
    """Abstract interface for where backup files get placed."""

    @abstractmethod
    def save(self, local_temp_path: str, destination_name: str) -> str:
        """
        Take a file that already exists at local_temp_path and place it
        into this storage backend under destination_name.
        Return the final location (path or URL) as a string.
        """
        raise NotImplementedError