import time

from squeak.core import CSqueak
from squeak.core import HASH_LENGTH
from squeak.core import MakeSqueakFromStr
from squeak.core.encryption import CDecryptionKey
from squeak.core.signing import CSigningKey

from squeakclient.squeaknode.core.blockchain import Blockchain


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

        return MakeSqueakFromStr(
            self.signing_key,
            content,
            block_height,
            block_hash,
            timestamp,
        )

    def clear_decryption_key(self, squeak: CSqueak) -> CSqueak:
        """Create a new CSqueak instance, with the decryption key cleared."""
        return CSqueak(
            hashEncContent=squeak.hashEncContent,
            hashReplySqk=squeak.hashReplySqk,
            hashBlock=squeak.hashBlock,
            nBlockHeight=squeak.nBlockHeight,
            scriptPubKey=squeak.scriptPubKey,
            vchEncryptionKey=squeak.vchEncryptionKey,
            vchEncDatakey=squeak.vchEncDatakey,
            vchIv=squeak.vchIv,
            nTime=squeak.nTime,
            nNonce=squeak.nNonce,
            encContent=squeak.encContent,
            scriptSig=squeak.scriptSig,
            vchDecryptionKey=b'',
        )

    def set_decryption_key(self, squeak: CSqueak, decryption_key: CDecryptionKey) -> CSqueak:
        """Create a new CSqueak instance, with the decryption key set."""
        return CSqueak(
            hashEncContent=squeak.hashEncContent,
            hashReplySqk=squeak.hashReplySqk,
            hashBlock=squeak.hashBlock,
            nBlockHeight=squeak.nBlockHeight,
            scriptPubKey=squeak.scriptPubKey,
            vchEncryptionKey=squeak.vchEncryptionKey,
            vchEncDatakey=squeak.vchEncDatakey,
            vchIv=squeak.vchIv,
            nTime=squeak.nTime,
            nNonce=squeak.nNonce,
            encContent=squeak.encContent,
            scriptSig=squeak.scriptSig,
            vchDecryptionKey=decryption_key.serialize(),
        )
