from abc import ABC, abstractmethod

from squeakclient.squeaknode.core.stores.squeak_store import SqueakStore
from squeakclient.squeaknode.core.stores.key_store import KeyStore
from squeakclient.squeaknode.core.stores.follow_store import FollowStore


class Storage(ABC):
    """Access to storage of data needed for the node."""

    @abstractmethod
    def get_squeak_store(self) -> SqueakStore:
        pass

    @abstractmethod
    def get_key_store(self) -> KeyStore:
        pass

    @abstractmethod
    def get_follow_store(self) -> FollowStore:
        pass
