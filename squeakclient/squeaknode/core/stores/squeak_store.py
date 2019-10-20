from abc import ABC
from abc import abstractmethod
from typing import List

from squeak.core import CSqueak
from squeak.core import CSqueakHeader
from squeak.core import HASH_LENGTH
from squeak.net import CInterested
from squeak.net import CSqueakLocator


class SavedSqueak(object):

    def __init__(self, squeak: CSqueak, content: bytes) -> None:
        self.squeak = squeak
        self.content = content


class SqueakStore(ABC):
    """A store of all the sqeaks held by this node.

    Used by both buyer and seller.
    """

    @abstractmethod
    def get_hashes(self) -> List[bytes]:
        pass

    @abstractmethod
    def get_squeaks(self) -> List[CSqueak]:
        pass

    @abstractmethod
    def get_squeak(self, squeak_hash: bytes) -> CSqueak:
        pass

    @abstractmethod
    def add_squeak(self, squeak: CSqueak) -> None:
        pass

    @abstractmethod
    def remove_squeak(self, squeak_hash: bytes) -> None:
        pass

    @abstractmethod
    def get_squeak_headers_created_by(self, created_by: bytes) -> List[CSqueakHeader]:
        pass

    @abstractmethod
    def get_squeaks_by_locator(self, locator: CSqueakLocator) -> List[CSqueak]:
        pass

    def _squeak_in_locator(self, squeak: CSqueak, locator: CSqueakLocator) -> bool:
        for interested in locator.vInterested:
            if self._squeak_in_interested(squeak, interested):
                return True

    def _squeak_in_interested(self, squeak: CSqueak, interested: CInterested) -> bool:
        if squeak.GetAddress() != interested.address:
            return False
        elif interested.nMinBlockHeight != -1 and squeak.nBlockHeight < interested.nMinBlockHeight:
            return False
        elif interested.nMaxBlockHeight != -1 and squeak.nBlockHeight > interested.nMaxBlockHeight:
            return False
        elif interested.hashReplySqk != b'\x00'*HASH_LENGTH and squeak.hashReplySqk != interested.hashReplySqk:
            return False
        return True
