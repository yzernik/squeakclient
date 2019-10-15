# class BuyerInvoiceStore(ABC):
#     """A store of received invoices."""

#     @abstractmethod
#     def get_buyer_invoices(self) -> List[BuyerInvoice]:
#         pass

#     @abstractmethod
#     def get_buyer_invoice(self, offer_id: int) -> BuyerInvoice:
#         pass

#     @abstractmethod
#     def add_buyer_invoice(self, buyer_invoice: BuyerInvoice) -> None:
#         pass

#     @abstractmethod
#     def mark_buyer_invoice_paid(self, offer_id: int, paid: bool = True) -> None:
#         pass

#     @abstractmethod
#     def is_buyer_invoice_paid(self, offer_id: int) -> bool:
#         pass

#     @abstractmethod
#     def get_buyer_invoice_creation_time(self, offer_id: int) -> int:
#         pass

#     @abstractmethod
#     def get_buyer_invoice_payment_time(self, offer_id: int) -> int:
#         pass

#     @abstractmethod
#     def remove_buyer_invoice(self, offer_id: int) -> None:
#         pass
