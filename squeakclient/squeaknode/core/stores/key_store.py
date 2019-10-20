from abc import ABC
from abc import abstractmethod

from squeak.core.signing import CSigningKey


class KeyStore(ABC):
    """A store of the signing key
    """

    @abstractmethod
    def get_signing_key(self) -> CSigningKey:
        pass

    @abstractmethod
    def set_signing_key(self, signing_key: CSigningKey) -> None:
        pass

    @abstractmethod
    def remove_signing_key(self) -> None:
        pass
