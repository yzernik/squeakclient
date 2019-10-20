import time

from squeak.core import CSqueak
from squeak.core import HASH_LENGTH
from squeak.core import MakeSqueak
from squeak.core.signing import CSigningKey

from squeakclient.squeaknode.core.blockchain import Blockchain
from squeakclient.squeaknode.core.encoding import encode_content


class SqueakMaker(object):
    """A factory for creating squeaks"""

    def __init__(self, signing_key: CSigningKey, blockchain: Blockchain) -> None:
        self.signing_key = signing_key
        self.blockchain = blockchain

    def make_squeak(self, content: str, reply_to: bytes = b'\x00'*HASH_LENGTH) -> CSqueak:
        """Create a CSqueak instance.

        content: content of the squeak
        reply_to: hash of the reply_to squeak
        """
        block_height = self.blockchain.get_block_count()
        block_hash = self.blockchain.get_block_hash(block_height)
        timestamp = int(time.time())
        data = encode_content(content)

        return MakeSqueak(
            self.signing_key,
            data,
            block_height,
            block_hash,
            timestamp,
        )
