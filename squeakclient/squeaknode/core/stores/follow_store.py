from abc import ABC
from abc import abstractmethod
from typing import List

from squeak.core.signing import CSqueakAddress


class FollowStore(ABC):
    """A store of all the addresses being followed.
    """

    @abstractmethod
    def get_follows(self) -> List[CSqueakAddress]:
        pass

    @abstractmethod
    def add_follow(self, follow: CSqueakAddress) -> None:
        pass

    @abstractmethod
    def remove_follow(self, follow: CSqueakAddress) -> None:
        pass
