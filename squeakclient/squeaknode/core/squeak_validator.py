from squeak.core import CSqueak
from squeak.core import CSqueakHeader
from squeak.core import CheckSqueak
from squeak.core import CheckSqueakError
from squeak.core import CheckSqueakHeader
from squeak.core import CheckSqueakHeaderError

from squeakclient.squeaknode.core.blockchain import Blockchain


class SqueakValidator(object):
    """Used for validating squeaks"""

    def __init__(self, blockchain: Blockchain) -> None:
        self.blockchain = blockchain

    def validate_squeak_header(self, squeak_header: CSqueakHeader) -> bool:
        """Decide if a given squeak header is valid."""
        try:
            CheckSqueakHeader(squeak_header)
        except CheckSqueakHeaderError:
            return False
        return self.check_block(squeak_header)

    def validate_squeak(self, squeak: CSqueak) -> bool:
        """Decide if a given squeak is valid."""
        try:
            CheckSqueak(squeak)
        except CheckSqueakError:
            return False
        return self.check_block(squeak)

    def validate_encrypted_squeak(self, squeak: CSqueak) -> bool:
        """Decide if a given squeak is valid, without checking the decryption key."""
        try:
            CheckSqueak(squeak, skipDecryptionCheck=True)
        except CheckSqueakError:
            return False
        return self.check_block(squeak)

    def check_block(self, squeak_header: CSqueakHeader) -> bool:
        """Decide if the block height and block hash of a squeak header is valid."""
        block_height = squeak_header.nBlockHeight
        block_hash = squeak_header.hashBlock
        actual_block_hash = self.blockchain.get_block_hash(block_height)
        if actual_block_hash is None:
            return False
        return actual_block_hash == block_hash
