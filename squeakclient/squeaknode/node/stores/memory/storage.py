from squeakclient.squeaknode.core.stores.squeak_store import SqueakStore
from squeakclient.squeaknode.core.stores.key_store import KeyStore
from squeakclient.squeaknode.core.stores.follow_store import FollowStore
from squeakclient.squeaknode.core.stores.storage import Storage
from squeakclient.squeaknode.node.stores.memory.squeak_store import MemorySqueakStore
from squeakclient.squeaknode.node.stores.memory.key_store import MemoryKeyStore
from squeakclient.squeaknode.node.stores.memory.follow_store import MemoryFollowStore


class MemoryStorage(Storage):

    def __init__(self):
        self.squeak_store = MemorySqueakStore()
        self.key_store = MemoryKeyStore()
        self.follow_store = MemoryFollowStore()

    def get_squeak_store(self) -> SqueakStore:
        return self.squeak_store

    def get_key_store(self) -> KeyStore:
        return self.key_store

    def get_follow_store(self) -> FollowStore:
        return self.follow_store
