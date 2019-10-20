import os

import pytest
from squeak.core import CheckSqueak
from squeak.core import CheckSqueakDecryptionKeyError
from squeak.core import HASH_LENGTH
from squeak.core.signing import CSigningKey

from squeakclient.squeaknode.core.blockchain import Blockchain
from squeakclient.squeaknode.core.squeak_maker import SqueakMaker


@pytest.fixture
def signing_key():
    return CSigningKey.generate()


@pytest.fixture
def verifying_key(signing_key):
    return signing_key.get_verifying_key()


@pytest.fixture
def block_height():
    return 56789


@pytest.fixture
def block_hash():
    return os.urandom(HASH_LENGTH)


@pytest.fixture
def blockchain(block_height, block_hash):
    return MockBlockchain(block_height, block_hash)


class TestSqueakMaker(object):
    def test_make_squeak(self, signing_key, verifying_key, blockchain):
        maker = SqueakMaker(signing_key, blockchain)
        content = 'Hello world!'
        squeak = maker.make_squeak(content)

        CheckSqueak(squeak)

        assert squeak.nBlockHeight == blockchain.get_block_count()
        assert squeak.hashBlock == blockchain.get_block_hash(squeak.nBlockHeight)

        decrypted_content = squeak.GetDecryptedContentStr()

        assert decrypted_content == content

    def test_set_decryption_key(self, signing_key, verifying_key, blockchain):
        maker = SqueakMaker(signing_key, blockchain)
        content = 'Hello world!'
        squeak = maker.make_squeak(content)
        decryption_key = squeak.GetDecryptionKey()

        CheckSqueak(squeak)

        cleared_squeak = maker.clear_decryption_key(squeak)

        with pytest.raises(CheckSqueakDecryptionKeyError):
            CheckSqueak(cleared_squeak)

        updated_squeak = maker.set_decryption_key(cleared_squeak, decryption_key)

        CheckSqueak(updated_squeak)


class MockBlockchain(Blockchain):

    def __init__(self, block_height, block_hash):
        self.block_height = block_height
        self.block_hash = block_hash

    def get_block_count(self) -> int:
        return self.block_height

    def get_block_hash(self, block_height: int) -> bytes:
        return self.block_hash
