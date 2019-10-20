# class SellerInvoiceStore(ABC):
#     """A store of sent invoices."""
#     @abstractmethod
#     def get_seller_invoices(self) -> List[SellerInvoice]:
#         pass
#     @abstractmethod
#     def get_seller_invoice(self, offer_id: int) -> SellerInvoice:
#         pass
#     @abstractmethod
#     def add_seller_invoice(self, seller_invoice: SellerInvoice) -> None:
#         pass
#     @abstractmethod
#     def mark_seller_invoice_paid(self, offer_id: int, paid: bool = True) -> None:
#         pass
#     @abstractmethod
#     def is_seller_invoice_paid(self, offer_id: int) -> bool:
#         pass
#     @abstractmethod
#     def get_seller_invoice_creation_time(self, offer_id: int) -> int:
#         pass
#     @abstractmethod
#     def get_seller_invoice_payment_time(self, offer_id: int) -> int:
#         pass
#     @abstractmethod
#     def remove_seller_invoice(self, offer_id: int) -> None:
#         pass
