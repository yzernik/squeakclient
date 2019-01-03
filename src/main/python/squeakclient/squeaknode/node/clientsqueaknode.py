import logging
import threading

from squeakclient.squeaknode.core.stores.storage import Storage
from squeakclient.squeaknode.node.squeaknode import SqueakNode
from squeakclient.squeaknode.core.blockchain import Blockchain
from squeakclient.squeaknode.core.squeak_maker import SqueakMaker

from squeak.core.signing import CSigningKey
from squeak.core.signing import CSqueakAddress


logger = logging.getLogger(__name__)


class ClientSqueakNode(SqueakNode):
    """Network node that handles client commands.
    """

    def __init__(self, storage: Storage, blockchain: Blockchain) -> None:
        super().__init__(storage=storage)
        self.storage = storage
        self.blockchain = blockchain
        self.key_lock = threading.Lock()
        self.key_changed_callback = None

    def start(self):
        super().start()

    def get_signing_key(self):
        return self.storage.get_key_store().get_signing_key()

    def get_address(self):
        key = self.get_signing_key()
        return self.address_from_signing_key(key)

    def set_signing_key(self, signing_key):
        with self.key_lock:
            self.storage.get_key_store().set_signing_key(signing_key)
            self.on_key_changed()

    def generate_signing_key(self):
        signing_key = CSigningKey.generate()
        self.set_signing_key(signing_key)
        return signing_key

    def on_key_changed(self):
        if self.key_changed_callback:
            address = self.get_address()
            logger.info('New address: {}'.format(address))
            self.key_changed_callback(address)

    def listen_key_changed(self, callback):
        self.key_changed_callback = callback

    def address_from_signing_key(self, key):
        verifying_key = key.get_verifying_key()
        return CSqueakAddress.from_verifying_key(verifying_key)

    def make_squeak(self, content):
        logger.debug('Trying to make squeak with content: {}'.format(content))
        with self.key_lock:
            key = self.get_signing_key()
            if key is None:
                logger.error('Missing signing key.')
                raise MissingSigningKeyError()
            else:
                squeak_maker = SqueakMaker(key, self.blockchain)
                squeak = squeak_maker.make_squeak(content)
                logger.info('Made squeak: {}'.format(squeak))
                self.add_squeak(squeak)
                return squeak

    def add_squeak(self, squeak):
        self.storage.get_squeak_store().add_squeak(squeak)


class ClientNodeError(Exception):
    pass


class MissingSigningKeyError(ClientNodeError):
    def __str__(self):
        return 'Missing signing key.'
