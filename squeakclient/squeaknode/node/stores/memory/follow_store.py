from typing import List

from squeak.core.signing import CSqueakAddress

from squeakclient.squeaknode.core.stores.follow_store import FollowStore


class MemoryFollowStore(FollowStore):

    def __init__(self):
        self.follows: List[CSqueakAddress] = []

    def get_follows(self) -> List[CSqueakAddress]:
        return self.follows

    def add_follow(self, follow: CSqueakAddress) -> None:
        self.follows.append(follow)

    def remove_follow(self, follow: CSqueakAddress) -> None:
        self.follows.remove(follow)
