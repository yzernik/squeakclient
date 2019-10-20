from squeak.core import CheckSqueak
from squeak.core import CheckSqueakError
from squeak.core import CheckSqueakHeader
from squeak.core import CheckSqueakHeaderError
from squeak.core import CSqueak
from squeak.core import CSqueakHeader

from squeakclient.squeaknode.core.blockchain import Blockchain


class SqueakValidator(object):
    """Used for validating squeaks"""

    def __init__(self, blockchain: Blockchain) -> None:
        self.blockchain = blockchain

    def is_valid_squeak(self, squeak: CSqueak, skipDecryptionCheck: bool = False) -> bool:
        """Decide if the squeak is valid."""
        try:
            CheckSqueak(squeak)
        except CheckSqueakError:
            return False
        return self.has_valid_block(squeak)

    def is_valid_squeak_header(self, squeak_header: CSqueakHeader) -> bool:
        """Decide if the squeak header is valid."""
        try:
            CheckSqueakHeader(squeak_header)
        except CheckSqueakHeaderError:
            return False
        return self.has_valid_block(squeak_header)

    def has_valid_block(self, squeak_header: CSqueakHeader) -> bool:
        """Decide if the block height and block hash of a squeak header is valid."""
        block_height = squeak_header.nBlockHeight
        block_hash = squeak_header.hashBlock
        actual_block_hash = self.blockchain.get_block_hash(block_height)
        if actual_block_hash is None:
            return False
        return actual_block_hash == block_hash
