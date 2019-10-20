import os

import pytest
from squeak.core import HASH_LENGTH
from squeak.core.signing import CSigningKey

from squeakclient.squeaknode.core.blockchain import Blockchain
from squeakclient.squeaknode.core.squeak_maker import SqueakMaker
from squeakclient.squeaknode.core.squeak_validator import SqueakValidator


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


@pytest.fixture
def false_blockchain(block_height, block_hash):
    false_block_hash = os.urandom(HASH_LENGTH)
    return MockBlockchain(block_height, false_block_hash)


class TestSqueakValidator(object):
    def test_validate_squeak(self, signing_key, verifying_key, blockchain):
        validator = SqueakValidator(blockchain)
        maker = SqueakMaker(signing_key, blockchain)
        content = 'Hello world!'
        squeak = maker.make_squeak(content)

        assert validator.is_valid_squeak(squeak)

    def test_validate_squeak_header(self, signing_key, verifying_key, blockchain):
        validator = SqueakValidator(blockchain)
        maker = SqueakMaker(signing_key, blockchain)
        content = 'Hello world!'
        squeak_header = maker.make_squeak(content).get_header()

        assert validator.is_valid_squeak_header(squeak_header)

    def test_validate_squeak_invalid(self, signing_key, verifying_key, blockchain, false_blockchain):
        validator = SqueakValidator(blockchain)
        maker = SqueakMaker(signing_key, false_blockchain)
        content = 'Hello world!'
        squeak = maker.make_squeak(content)

        assert not validator.is_valid_squeak(squeak)

    def test_validate_squeak_header_invalid(self, signing_key, verifying_key, blockchain, false_blockchain):
        validator = SqueakValidator(blockchain)
        maker = SqueakMaker(signing_key, false_blockchain)
        content = 'Hello world!'
        squeak_header = maker.make_squeak(content).get_header()

        assert not validator.is_valid_squeak_header(squeak_header)

    def test_validate_squeak_invalid_decryption_key(self, signing_key, verifying_key, blockchain):
        validator = SqueakValidator(blockchain)
        maker = SqueakMaker(signing_key, blockchain)
        content = 'Hello world!'
        squeak = maker.make_squeak(content)
        cleared_squeak = maker.clear_decryption_key(squeak)

        assert not validator.is_valid_squeak(cleared_squeak)


class MockBlockchain(Blockchain):

    def __init__(self, block_height, block_hash):
        self.block_height = block_height
        self.block_hash = block_hash

    def get_block_count(self) -> int:
        return self.block_height

    def get_block_hash(self, block_height: int) -> bytes:
        return self.block_hash
