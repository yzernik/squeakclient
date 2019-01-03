import socket
import time
import threading
import logging

import squeak.params
from squeak.messages import msg_getaddr

from squeakclient.squeaknode.node.peer import Peer


MIN_PEERS = 5
MAX_PEERS = 10
UPDATE_THREAD_SLEEP_TIME = 10


logger = logging.getLogger(__name__)


class PeerNode(object):
    """Network node that connnects to other peers in the network.
    """

    def __init__(self, min_peers=MIN_PEERS, max_peers=MAX_PEERS, port=None):
        self.peers = {}
        self.min_peers = min_peers
        self.max_peers = max_peers
        self.peers_lock = threading.Lock()
        self.peers_changed_callback = None
        self.ip = socket.gethostbyname('localhost')
        self.port = port or squeak.params.params.DEFAULT_PORT

    def start(self):
        # Start Listen thread
        threading.Thread(target=self.accept_connections).start()

        # Start Update thread
        threading.Thread(target=self.update).start()

    def update(self):
        """Periodic task that keeps peers updated."""
        while True:
            # Disconnect from unhealthy peers
            for peer in list(self.peers.values()):
                peer.health_check()

            # Connect to more peers
            if len(self.peers) < self.min_peers:
                logger.debug('Broadcasting getaddr')
                self.broadcast_msg(msg_getaddr())

                logger.debug('Connecting to seed peers.')
                for seed_peer in get_seed_peer_addresses():
                    self.add_address(seed_peer)

            # Sleep
            time.sleep(UPDATE_THREAD_SLEEP_TIME)

    def accept_connections(self):
        listen_socket = socket.socket()
        listen_socket.bind(('', self.port))
        listen_socket.listen()
        while True:
            logger.info('waiting for connection')
            peer_socket, address = listen_socket.accept()
            peer_socket.setblocking(True)
            peer = Peer(peer_socket, address)
            self.handle_connection(peer)

    def make_connection(self, ip, port):
        address = (ip, port)
        logger.debug('Making connection to {}'.format(address))
        try:
            peer_socket = socket.socket()
            peer_socket.connect(address)
            peer_socket.setblocking(True)
            peer = Peer(peer_socket, address, outgoing=True)
            self.handle_connection(peer)
            self.on_connect(peer)
        except Exception:
            pass

    def handle_connection(self, peer):
        with self.peers_lock:
            if peer.outgoing:
                if len(self.peers) >= self.max_peers or peer.address in self.peers:
                    peer.close()
                    logger.debug('Failed to connect to peer {}'.format(peer))
                    return
            self.peers[peer.address] = peer
            self.on_peers_changed()
        threading.Thread(
            target=self.handle_peer,
            args=(peer,),
        ).start()

    def handle_peer(self, peer):
        """Listens on the peer_socket of the peer.
        """
        while True:
            try:
                peer.handle_recv_data(self.handle_msg)
            except Exception:
                peer.peer_socket.close()
                with self.peers_lock:
                    del self.peers[peer.address]
                    logger.debug('Removed peer {}'.format(peer))
                    self.on_peers_changed()
                return False

    def send_msg(self, peer, msg):
        peer.send_msg(msg)

    def broadcast_msg(self, msg):
        for peer in list(self.peers.values()):
            self.send_msg(peer, msg)

    def add_address(self, address):
        """Add a new address."""
        if len(self.peers) >= self.max_peers:
            return
        self.connect_address(address)

    def connect_address(self, address):
        """Connect to new address."""
        logger.debug('Connecting to peer with address {}'.format(address))
        if address in self.peers:
            return
        ip, port = address
        threading.Thread(
            target=self.make_connection,
            args=(ip, port),
        ).start()

    def connect_host(self, host):
        """Connect to new host."""
        ip = socket.gethostbyname(host)
        address = (ip, squeak.params.params.DEFAULT_PORT)
        self.connect_address(address)

    def on_peers_changed(self):
        logger.info('Connected number of peers {}'.format(len(self.peers.keys())))
        if self.peers_changed_callback:
            peers = list(self.peers.values())
            self.peers_changed_callback(peers)

    def listen_peers_changed(self, callback):
        self.peers_changed_callback = callback

    def handle_msg(self, msg, peer):
        """Main message handler.
        """
        pass

    def on_connect(self, peer):
        """Action to take when a new peer connection is made.
        """
        pass


def resolve_hostname(hostname):
    """Get the ip address from hostname."""
    try:
        ip = socket.gethostbyname(hostname)
    except Exception:
        return None
    port = squeak.params.params.DEFAULT_PORT
    return (ip, port)


def get_seed_peer_addresses():
    """Get addresses of seed peers"""
    for _, seed_host in squeak.params.params.DNS_SEEDS:
        address = resolve_hostname(seed_host)
        if address:
            yield address
