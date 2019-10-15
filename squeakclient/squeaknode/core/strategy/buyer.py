from abc import ABC, abstractmethod
from typing import List

from bitcoin.net import CAddress

from squeak.core import CSqueak
from squeak.core.net import CInterested


class Buyer(ABC):
    """Used to decide if a squeak should be bought or not."""

    @abstractmethod
    def get_buy_decision(self, squeak: CSqueak, price: int, peer: CAddress) -> bool:
        pass

    @abstractmethod
    def get_interesteds(self, peer: CAddress) -> List[CInterested]:
        pass
