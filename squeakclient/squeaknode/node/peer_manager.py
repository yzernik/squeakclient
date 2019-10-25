import logging
import socket
import threading
import time

import squeak.params

from squeakclient.squeaknode.node.peer import Peer
from squeakclient.squeaknode.node.peer_message_handler import PeerMessageHandler
from squeakclient.squeaknode.node.peer_controller import PeerController


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
        # self.peer_msg_handler = None

    def start(self, peers_access, squeaks_access):
        # self.peer_msg_handler = peer_msg_handler
        self.peers_access = peers_access
        self.squeaks_access = squeaks_access

        # Start Listen thread
        threading.Thread(target=self.accept_connections).start()

        # Start Update thread
        threading.Thread(target=self.update).start()

    def update(self):
        """Periodic task that keeps peers updated."""
        while True:
            logger.info('Running update thread.')

            # Disconnect from unhealthy peers
            # TODO move this to a different thread, one per peer.
            for peer in list(self.connection_manager.peers):
                if peer.has_handshake_timeout():
                    logger.info('Closing peer because of handshake timeout {}'.format(peer))
                    peer.close()
                if peer.has_inactive_timeout():
                    logger.info('Closing peer because of last message timeout {}'.format(peer))
                    peer.close()
                if peer.has_ping_timeout():
                    logger.info('Closing peer because of ping timeout {}'.format(peer))
                    peer.close()

                # Check if it's time to send a ping.
                if peer.is_time_for_ping():
                    peer_controller = PeerController(peer, self.peers_access, self.squeaks_access)
                    peer_controller.initiate_ping()

            # Connect to more peers
            if len(self.get_connected_peers()) == 0:
                self.connect_seed_peers()

            # Sleep
            time.sleep(UPDATE_THREAD_SLEEP_TIME)

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
        peer_msg_handler = PeerMessageHandler(peer, self.connection_manager, self.peers_access, self.squeaks_access)
        threading.Thread(
            target=peer_msg_handler.start,
        ).start()

    # def handle_peer_msgs(self, peer):
    #     """Listens on the peer_socket of the peer.
    #     """
    #     peer_msg_handler = PeerMessageHandler(peer, self.connection_manager, self.peers_access, self.squeaks_access)
    #     while True:
    #         try:
    #             peer_msg_handler.handle_msgs()
    #         except Exception as e:
    #             logger.exception('Error in handle_peer: {}'.format(e))
    #             peer.close()
    #             self.connection_manager.remove_peer(peer)
    #             return

    # def handle_peer_updates(self, peer):
    #     """Run periodic tasks on the peer.
    #     """
    #     peer_msg_handler = PeerMessageHandler(peer, self.peers_access, self.squeaks_access)
    #     while True:
    #         try:
    #             peer_msg_handler.handle_msgs()
    #         except Exception as e:
    #             logger.exception('Error in handle_peer: {}'.format(e))
    #             peer.close()
    #             self.connection_manager.remove_peer(peer)
    #             return

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

    # def on_connect(self, peer):
    #     """Action to take when a new peer connection is made.
    #     """
    #     logger.debug('Calling on_connect with {}'.format(peer))
    #     peer_controller = PeerController(peer, self.peers_access, self.squeaks_access)
    #     peer_controller.initiate_handshake()

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
