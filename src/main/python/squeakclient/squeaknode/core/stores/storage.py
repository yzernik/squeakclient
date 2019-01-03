from abc import ABC, abstractmethod

from squeakclient.squeaknode.core.stores.squeak_store import SqueakStore
from squeakclient.squeaknode.core.stores.key_store import KeyStore


class Storage(ABC):
    """Access to storage of data needed for the node."""

    @abstractmethod
    def get_squeak_store(self) -> SqueakStore:
        pass

    @abstractmethod
    def get_key_store(self) -> KeyStore:
        pass
