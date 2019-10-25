import logging
import threading


MIN_PEERS = 5
MAX_PEERS = 10
UPDATE_THREAD_SLEEP_TIME = 10


logger = logging.getLogger(__name__)


class ConnectionManager(object):
    """Maintains connections to other peers in the network.
    """

    def __init__(self, min_peers=MIN_PEERS, max_peers=MAX_PEERS, port=None):
        self._peers = {}
        self.min_peers = min_peers
        self.max_peers = max_peers
        self.peers_lock = threading.Lock()
        self.peers_changed_callback = None
        self.peer_msg_handler = None

    @property
    def peers(self):
        return list(self._peers.values())

    @property
    def handshaked_peers(self):
        return [
            peer
            for peer in self.peers
            if peer.handshake_complete
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
        logger.info('Current number of peers with handshake {}'.format(len(self.handshaked_peers)))
        if self.peers_changed_callback:
            peers = self.get_connected_peers()
            self.peers_changed_callback(peers)

    def listen_peers_changed(self, callback):
        self.peers_changed_callback = callback

    def add_peer(self, peer):
        """Add a peer.

        Return True if successfully added.
        """
        with self.peers_lock:
            if peer.outgoing:
                if len(self.peers) >= self.max_peers or self.has_connection(peer.address):
                    peer.close()
                    logger.debug('Failed to connect to peer {}'.format(peer))
                    return False
            self._peers[peer.address] = peer
            logger.debug('Added peer {}'.format(peer))
            self.on_peers_changed()
            return True

    def remove_peer(self, peer):
        """Add a peer.

        Return True if successfully added.
        """
        with self.peers_lock:
            del self._peers[peer.address]
            logger.debug('Removed peer {}'.format(peer))
            self.on_peers_changed()

    def need_more_peers(self):
        """Return True if more peers are needed."""
        return len(self.handshaked_peers) < self.max_peers
