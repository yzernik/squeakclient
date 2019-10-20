# class OfferRequestStore(ABC):
#     """A store of all the offers that have been requested."""
#     @abstractmethod
#     def get_offer_requests(self) -> List[OfferRequest]:
#         pass
#     @abstractmethod
#     def get_offer_request(self, request_id: int) -> OfferRequest:
#         pass
#     @abstractmethod
#     def add_offer_request(self, offer_request: OfferRequest) -> None:
#         pass
#     @abstractmethod
#     def remove_offer_request(self, request_id: int) -> None:
#         pass
