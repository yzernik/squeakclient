from abc import ABC
from abc import abstractmethod
from typing import List

from bitcoin.net import CAddress


class OfferRequest(object):
    """A request for an offer from another peer.

    Used by the buyer.
    """

    def __init__(self, request_id: int, squeak_hash: bytes, proof: bytes, challenge: bytes, peer: CAddress) -> None:
        self.request_id = request_id
        self.squeak_hash = squeak_hash
        self.proof = proof
        self.challenge = challenge
        self.peer = peer


class OfferRequestStore(ABC):
    """A store of all the offers that have been requested."""

    @abstractmethod
    def get_offer_requests(self) -> List[OfferRequest]:
        pass

    @abstractmethod
    def get_offer_request(self, request_id: int) -> OfferRequest:
        pass

    @abstractmethod
    def add_offer_request(self, offer_request: OfferRequest) -> None:
        pass

    @abstractmethod
    def remove_offer_request(self, request_id: int) -> None:
        pass
