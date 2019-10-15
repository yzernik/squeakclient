from abc import ABC, abstractmethod
from typing import List

from bitcoin.net import CAddress

from squeak.core import CSqueakHeader


class BuyerInvoice(object):
    """An invoice received from a seller.

    Used by the buyer.
    """

    def __init__(self, offer_id: int, squeak_header: CSqueakHeader, price: int, payment_info: str, peer: CAddress) -> None:
        self.offer_id = offer_id
        self.squeak_header = squeak_header
        self.price = price
        self.payment_info = payment_info
        self.peer = peer


class BuyerInvoiceStore(ABC):
    """A store of received invoices."""

    @abstractmethod
    def get_buyer_invoices(self) -> List[BuyerInvoice]:
        pass

    @abstractmethod
    def get_buyer_invoice(self, offer_id: int) -> BuyerInvoice:
        pass

    @abstractmethod
    def add_buyer_invoice(self, buyer_invoice: BuyerInvoice) -> None:
        pass

    @abstractmethod
    def mark_buyer_invoice_fulfilled(self, offer_id: int, paid: bool = True) -> None:
        pass

    @abstractmethod
    def is_buyer_invoice_fulfilled(self, offer_id: int) -> bool:
        pass

    @abstractmethod
    def get_buyer_invoice_creation_time(self, offer_id: int) -> int:
        pass

    @abstractmethod
    def get_buyer_invoice_fulfillment_time(self, offer_id: int) -> int:
        pass

    @abstractmethod
    def remove_buyer_invoice(self, offer_id: int) -> None:
        pass
