from abc import ABC, abstractmethod


class LightningClient(ABC):
    """Used to get interact with the lightning wallet."""

    @abstractmethod
    def get_block_height(self) -> int:
        pass

    @abstractmethod
    def get_block_hash(self) -> bytes:
        pass
