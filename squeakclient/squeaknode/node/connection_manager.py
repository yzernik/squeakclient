import logging
import threading


MIN_PEERS = 5
MAX_PEERS = 10
UPDATE_THREAD_SLEEP_TIME = 10


logger = logging.getLogger(__name__)


class ConnectionManager(object):
    """Maintains connections to other peers in the network.
    """

    def __init__(self):
        self._peers = {}
        self.peers_lock = threading.Lock()
        self.peers_changed_callback = None

    @property
    def peers(self):
        return [
            peer
            for peer in list(self._peers.values())
            if peer.is_handshake_complete
        ]

    def has_connection(self, address):
        """Return True if the address is already connected."""
        return address in self._peers

    def has_local_version_nonce(self, nonce):
        """Return True if the nonce is one of the local version nonces."""
        for peer in self.peers:
            if peer.local_version:
                if nonce == peer.local_version.nNonce:
                    return True
        return False

    def on_peers_changed(self):
        logger.info('Current number of peers {}'.format(len(self.peers)))
        if self.peers_changed_callback:
            peers = self.get_connected_peers()
            self.peers_changed_callback(peers)

    def listen_peers_changed(self, callback):
        self.peers_changed_callback = callback

    def add_peer(self, peer):
        """Add a peer.
        """
        with self.peers_lock:
            if self.has_connection(peer.address):
                logger.debug('Failed to add peer {}'.format(peer))
                raise DuplicatePeerError()
            self._peers[peer.address] = peer
            logger.debug('Added peer {}'.format(peer))
            self.on_peers_changed()

    def remove_peer(self, peer):
        """Add a peer.
        """
        with self.peers_lock:
            if not self.has_connection(peer.address):
                logger.debug('Failed to remove peer {}'.format(peer))
                raise MissingPeerError()
            else:
                del self._peers[peer.address]
                logger.debug('Removed peer {}'.format(peer))
                self.on_peers_changed()

    def need_more_peers(self):
        """Return True if more peers are needed."""
        return len(self.peers) < self.max_peers


class DuplicatePeerError(Exception):
    pass


class MissingPeerError(Exception):
    pass
