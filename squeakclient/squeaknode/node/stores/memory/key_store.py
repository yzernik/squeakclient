from typing import Optional

from squeak.core.signing import CSigningKey

from squeakclient.squeaknode.core.stores.key_store import KeyStore


class MemoryKeyStore(KeyStore):

    def __init__(self):
        self.signing_key = None

    def get_signing_key(self) -> Optional[CSigningKey]:
        return self.signing_key

    def set_signing_key(self, signing_key: CSigningKey) -> None:
        self.signing_key = signing_key

    def remove_signing_key(self) -> None:
        self.signing_key = None
