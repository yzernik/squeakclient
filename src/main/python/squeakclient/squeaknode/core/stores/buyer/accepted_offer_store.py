from abc import ABC, abstractmethod
from typing import List

from bitcoin.net import CAddress

from squeak.core.squeak import CSqueak


class AcceptedOffer(object):
    """An offer that has been accepted.

    Used by the buyer.
    """

    def __init__(self, offer_id: int, squeak: CSqueak, price: int, peer: CAddress) -> None:
        self.offer_id = offer_id
        self.squeak = squeak
        self.price = price
        self.peer = peer


class OfferRequestStore(ABC):
    """A store of all the offers that have been requested."""

    @abstractmethod
    def get_accepted_offer(self) -> List[AcceptedOffer]:
        pass

    @abstractmethod
    def add_accepted_offer(self, accepted_offer: AcceptedOffer) -> None:
        pass

    @abstractmethod
    def remove_accepted_offer(self, offer_id: int) -> None:
        pass
