from abc import ABC, abstractmethod

from bitcoin.net import CAddress

from squeak.core import CSqueak


class Seller(ABC):
    """Used to decide on a price to sell a squeak."""

    @abstractmethod
    def get_sell_price(self, squeak: CSqueak, peer: CAddress) -> int:
        pass
