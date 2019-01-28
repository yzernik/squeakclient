import logging
import threading
import time

from squeakclient.squeaknode.node.access import SigningKeyAccess
from squeakclient.squeaknode.node.access import FollowsAccess
from squeakclient.squeaknode.node.access import SqueaksAccess
from squeakclient.squeaknode.core.blockchain import Blockchain
from squeakclient.squeaknode.core.squeak_maker import SqueakMaker
from squeakclient.squeaknode.core.stores.storage import Storage
from squeakclient.squeaknode.node.handshakenode import HandshakeNode
from squeakclient.squeaknode.node.squeaknode import ClientPeerMessageHandler

from squeak.messages import msg_getsqueaks


UPDATE_THREAD_SLEEP_TIME = 10


logger = logging.getLogger(__name__)


class ClientSqueakNode(object):
    """Network node that handles client commands.
    """

    def __init__(self, storage: Storage, blockchain: Blockchain) -> None:
        self.storage = storage
        self.blockchain = blockchain
        self.peer_node = HandshakeNode()
        self.signing_key_access = SigningKeyAccess(self.storage)
        self.follows_access = FollowsAccess(self.storage)
        self.squeaks_access = SqueaksAccess(self.storage)
        self.peer_msg_handler = ClientPeerMessageHandler(self.peer_node, self.squeaks_access)

    def start(self):
        # Start network node
        self.peer_node.start(
            self.peer_msg_handler,
        )

        # Start Update thread
        threading.Thread(target=self.update).start()

    def update(self):
        """Periodic task updates client."""
        while True:
            # Fetch data from other peers.
            self.find_squeaks()

            # Sleep
            time.sleep(UPDATE_THREAD_SLEEP_TIME)

    def get_signing_key(self):
        return self.signing_key_access.get_signing_key()

    def get_address(self):
        return self.signing_key_access.get_address()

    def set_signing_key(self, signing_key):
        self.signing_key_access.set_signing_key(signing_key)

    def generate_signing_key(self):
        self.signing_key_access.generate_signing_key()

    def listen_key_changed(self, callback):
        self.signing_key_access.listen_key_changed(callback)

    def make_squeak(self, content):
        logger.debug('Trying to make squeak with content: {}'.format(content))
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
        self.squeaks_access.add_squeak(squeak)

    def listen_squeaks_changed(self, callback):
        self.squeaks_access.listen_squeaks_changed(callback)

    def add_follow(self, follow):
        self.follows_access.add_follow(follow)

    def listen_follows_changed(self, callback):
        self.follows_access.listen_follows_changed(callback)

    def get_follows(self):
        self.follows_access.get_follows()

    def find_squeaks(self):
        locator = self.follows_access.get_follow_locator()
        getsqueaks = msg_getsqueaks(locator=locator)
        self.peer_node.broadcast_msg(getsqueaks)


class ClientNodeError(Exception):
    pass


class MissingSigningKeyError(ClientNodeError):
    def __str__(self):
        return 'Missing signing key.'
