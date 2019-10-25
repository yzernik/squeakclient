import logging

from squeakclient.squeaknode.core.blockchain import Blockchain
from squeakclient.squeaknode.core.lightning_client import LightningClient
from squeakclient.squeaknode.core.squeak_maker import SqueakMaker
from squeakclient.squeaknode.core.stores.storage import Storage
from squeakclient.squeaknode.node.access import FollowsAccess
from squeakclient.squeaknode.node.access import PeersAccess
from squeakclient.squeaknode.node.access import SigningKeyAccess
from squeakclient.squeaknode.node.access import SqueaksAccess
from squeakclient.squeaknode.node.peer_manager import PeerManager
from squeakclient.squeaknode.node.connection_manager import ConnectionManager
from squeakclient.squeaknode.node.peer_handler import PeerHandler


UPDATE_THREAD_SLEEP_TIME = 10


logger = logging.getLogger(__name__)


class ClientSqueakNode(object):
    """Network node that handles client commands.
    """

    def __init__(self, storage: Storage, blockchain: Blockchain, lightning_client: LightningClient) -> None:
        self.storage = storage
        self.blockchain = blockchain
        self.lightning_client = lightning_client
        self.connection_manager = ConnectionManager()
        self.peer_manager = PeerManager(self.connection_manager)
        self.peers_access = PeersAccess(self.peer_manager)
        self.signing_key_access = SigningKeyAccess(self.storage)
        self.follows_access = FollowsAccess(self.storage)
        self.squeaks_access = SqueaksAccess(self.storage)
        self.peer_handler = PeerHandler(self.connection_manager, self.peer_manager, self.squeaks_access)

    def start(self):
        # Start network node
        self.peer_manager.start(
            self.peer_handler,
        )

    def get_signing_key(self):
        return self.signing_key_access.get_signing_key()

    def get_address(self):
        return self.signing_key_access.get_address()

    def set_signing_key(self, signing_key):
        self.signing_key_access.set_signing_key(signing_key)

    def generate_signing_key(self):
        return self.signing_key_access.generate_signing_key()

    def listen_key_changed(self, callback):
        self.signing_key_access.listen_key_changed(callback)

    def make_squeak(self, content):
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

    def connect_host(self, host):
        self.peers_access.connect_host(host)

    def get_peers(self):
        return self.peers_access.get_connected_peers()

    def listen_peers_changed(self, callback):
        self.peers_access.listen_peers_changed(callback)

    def get_wallet_balance(self):
        return self.lightning_client.get_wallet_balance()


class ClientNodeError(Exception):
    pass


class MissingSigningKeyError(ClientNodeError):
    def __str__(self):
        return 'Missing signing key.'
