from abc import ABC, abstractmethod
from typing import List

from bitcoin.net import CAddress


class Offer(object):
    """An offer made to another peer.

    Used by the seller.
    """

    def __init__(self, offer_id: int, request_id: int, squeak_hash: bytes, price: int, peer: CAddress) -> None:
        self.offer_id = offer_id
        self.request_id = request_id
        self.squeak_hash = squeak_hash
        self.price = price
        self.peer


class OfferStore(ABC):
    """A store of all the offers that have been created.

    Used by the seller.
    """

    @abstractmethod
    def get_offers(self) -> List[Offer]:
        pass

    @abstractmethod
    def add_offer(self, offer_request: Offer) -> None:
        pass

    @abstractmethod
    def remove_offer(self, request_id: int) -> None:
        pass
