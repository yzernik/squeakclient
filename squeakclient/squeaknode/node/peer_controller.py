import time
import logging

from squeak.messages import msg_ping
from squeak.messages import msg_version

from squeakclient.squeaknode.util import generate_nonce
from squeakclient.squeaknode.node.peer import Peer


logger = logging.getLogger(__name__)


UPDATE_TIME_INTERVAL = 10
HANDSHAKE_VERSION = 70002


class PeerController():
    """Commands for interacting with remote peer.
    """

    def __init__(self, peer: Peer, peers_access, squeaks_access) -> None:
        super().__init__()
        self.peer = peer
        self.peers_access = peers_access
        self.squeaks_access = squeaks_access

    def initiate_handshake(self):
        """Action to take upon completion of handshake with a peer."""
        logger.debug('Starting handshake with {}'.format(self.peer))
        version = self.version_pkt()
        self.peer.set_local_version(version)
        self.peers_access.send_msg(self.peer, version)

    def initiate_ping(self):
        """Send a ping message and expect a pong response."""
        logger.debug('Sending a ping to {}'.format(self.peer))
        nonce = generate_nonce()
        ping = msg_ping()
        ping.nonce = nonce
        self.peers_access.send_msg(self.peer, ping)
        self.peer.set_last_sent_ping(nonce)

    def version_pkt(self):
        msg = msg_version()
        local_ip, local_port = self.peers_access.get_local_ip_port()
        server_ip, server_port = self.peer.address
        msg.nVersion = HANDSHAKE_VERSION
        msg.addrTo.ip = server_ip
        msg.addrTo.port = server_port
        msg.addrFrom.ip = local_ip
        msg.addrFrom.port = local_port
        msg.nNonce = generate_nonce()
        return msg


# class PeerUpdater():
#     """Handles incoming messages from peers.
#     """

#     def __init__(self, peer: Peer, peers_access, squeaks_access, update_time_interval=UPDATE_TIME_INTERVAL) -> None:
#         super().__init__()
#         self.peer = peer
#         self.peers_access = peers_access
#         self.squeaks_access = squeaks_access
#         self.peer_controller = PeerController(self.peer, self.peers_access, self.squeaks_access)
#         self.update_time_interval = update_time_interval

#     def update(self):
#         """Keep the peer connection updated."""

#         # Disconnect from peer if unhealthy
#         if self.peer.has_handshake_timeout():
#             logger.info('Closing peer because of handshake timeout {}'.format(self.peer))
#             self.peer.close()
#         if self.peer.has_inactive_timeout():
#             logger.info('Closing peer because of last message timeout {}'.format(self.peer))
#             self.peer.close()
#         if self.peer.has_ping_timeout():
#             logger.info('Closing peer because of ping timeout {}'.format(self.peer))
#             self.peer.close()

#         # Check if it's time to send a ping.
#         if self.peer.is_time_for_ping():
#             self.peer_controller.initiate_ping()

#         # Sleep
#         time.sleep(self.update_time_interval)
