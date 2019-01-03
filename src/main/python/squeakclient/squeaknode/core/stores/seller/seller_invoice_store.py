from abc import ABC, abstractmethod
from typing import List

from bitcoin.net import CAddress

from squeak.core import CSqueakHeader


class SellerInvoice(object):
    """An invoice sent to a buyer.

    Used by the seller.
    """

    def __init__(self, offer_id: int, squeak_header: CSqueakHeader, price: int, payment_info: str, peer: CAddress) -> None:
        self.offer_id = offer_id
        self.squeak_header = squeak_header
        self.price = price
        self.payment_info = payment_info
        self.peer = peer


class SellerInvoiceStore(ABC):
    """A store of sent invoices."""

    @abstractmethod
    def get_seller_invoices(self) -> List[SellerInvoice]:
        pass

    @abstractmethod
    def get_seller_invoice(self, offer_id: int) -> SellerInvoice:
        pass

    @abstractmethod
    def add_seller_invoice(self, seller_invoice: SellerInvoice) -> None:
        pass

    @abstractmethod
    def mark_seller_invoice_paid(self, offer_id: int, paid: bool = True) -> None:
        pass

    @abstractmethod
    def is_seller_invoice_paid(self, offer_id: int) -> bool:
        pass

    @abstractmethod
    def get_seller_invoice_creation_time(self, offer_id: int) -> int:
        pass

    @abstractmethod
    def get_seller_invoice_payment_time(self, offer_id: int) -> int:
        pass

    @abstractmethod
    def remove_seller_invoice(self, offer_id: int) -> None:
        pass
