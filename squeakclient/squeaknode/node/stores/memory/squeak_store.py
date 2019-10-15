from typing import List
from typing import Mapping

from squeak.core import CSqueak
from squeak.core import CSqueakHeader
from squeak.net import CSqueakLocator

from squeakclient.squeaknode.core.stores.squeak_store import SqueakStore


class MemorySqueakStore(SqueakStore):

    def __init__(self):
        self.squeaks: Mapping[bytes, CSqueak] = {}

    def get_hashes(self) -> List[bytes]:
        return list(self.squeaks.keys())

    def get_squeaks(self) -> List[CSqueak]:
        return list(self.squeaks.values())

    def get_squeak(self, squeak_hash: bytes) -> CSqueak:
        return self.squeaks.get(squeak_hash)

    def add_squeak(self, squeak: CSqueak) -> None:
        key = squeak.GetHash()
        self.squeaks[key] = squeak

    def remove_squeak(self, squeak_hash: bytes) -> None:
        del self.squeaks[squeak_hash]

    def get_squeak_headers_created_by(self, created_by: bytes) -> List[CSqueakHeader]:
        return [saved_squeak for saved_squeak
                in self.squeaks
                if saved_squeak.squeak.vchPubkey == created_by]

    def get_squeaks_by_locator(self, locator: CSqueakLocator) -> List[CSqueak]:
        return [squeak for hash, squeak
                in self.squeaks.items()
                if self._squeak_in_locator(squeak, locator)]
