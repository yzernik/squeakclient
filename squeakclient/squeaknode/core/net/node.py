from typing import List

from squeak.core.advertised_squeak import AdvertisedSqueak
from squeak.core.squeak import Squeak
from squeak.core.squeak_store import SqueakStore


class Node(object):

    def __init__(self, squeak_store: SqueakStore) -> None:
        self.squeak_store = squeak_store

    def on_squeak_received(self, squeak: Squeak) -> None:
        if squeak.has_valid_signature:
            self.squeak_store.add_squeak(squeak)

    def on_advertised_squeaks_received(self, advertised_squeak: AdvertisedSqueak) -> None:
        pass

    def get_follows(self) -> List[str]:
        pass

    def get_squeaks(self) -> List[Squeak]:
        return self.squeak_store.get_squeaks()
