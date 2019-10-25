import logging
import socket
import threading

import squeak.params

from squeakclient.squeaknode.node.peer import Peer


MIN_PEERS = 5
MAX_PEERS = 10
UPDATE_THREAD_SLEEP_TIME = 10


logger = logging.getLogger(__name__)


class PeerManager(object):
    """Maintains connections to other peers in the network.
    """

    def __init__(self, connection_manager, port=None):
        self.ip = socket.gethostbyname('localhost')
        self.port = port or squeak.params.params.DEFAULT_PORT
        self.connection_manager = connection_manager

    def start(self, peer_handler):
        self.peer_handler = peer_handler

        # Start Listen thread
        threading.Thread(target=self.accept_connections).start()

    def accept_connections(self):
        listen_socket = socket.socket()
        listen_socket.bind(('', self.port))
        listen_socket.listen()
        while True:
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
            # self.on_connect(peer)
        except Exception:
            pass

    def handle_connection(self, peer):
        threading.Thread(
            target=self.peer_handler.start,
            args=(peer,),
        ).start()

    def add_address(self, address):
        """Add a new address."""
        if self.connection_manager.need_more_peers():
            self.connect_address(address)

    def connect_address(self, address):
        """Connect to new address."""
        logger.debug('Connecting to peer with address {}'.format(address))
        if self.connection_manager.has_connection(address):
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

    def connect_seed_peers(self):
        """Find more peers.
        """
        for seed_peer in get_seed_peer_addresses():
            self.add_address(seed_peer)

    def get_connected_peers(self):
        return self.connection_manager.handshaked_peers


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
