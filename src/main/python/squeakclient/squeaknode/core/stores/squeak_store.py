from abc import ABC, abstractmethod
from typing import List

from squeak.core import CSqueak
from squeak.core import CSqueakHeader


class SavedSqueak(object):

    def __init__(self, squeak: CSqueak, content: bytes) -> None:
        self.squeak = squeak
        self.content = content


class SqueakStore(ABC):
    """A store of all the sqeaks held by this node.

    Used by both buyer and seller.
    """

    @abstractmethod
    def get_squeaks(self) -> List[bytes]:
        pass

    @abstractmethod
    def get_squeak(self, bytes) -> CSqueak:
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
