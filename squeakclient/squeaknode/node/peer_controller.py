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

    def __init__(self, peer: Peer, connection_manager, peer_manager, squeaks_access) -> None:
        super().__init__()
        self.peer = peer
        self.connection_manager = connection_manager
        self.peer_manager = peer_manager
        self.squeaks_access = squeaks_access

    def initiate_handshake(self):
        """Action to take upon completion of handshake with a peer."""
        logger.debug('Starting handshake with {}'.format(self.peer))
        version = self.version_pkt()
        self.peer.set_local_version(version)
        self.peer.send_msg(version)

    def initiate_ping(self):
        """Send a ping message and expect a pong response."""
        nonce = generate_nonce()
        ping = msg_ping()
        ping.nonce = nonce
        self.peer.send_msg(ping)
        self.peer.set_last_sent_ping(nonce)

    def version_pkt(self):
        msg = msg_version()
        local_ip, local_port = self.peer_manager.ip, self.peer_manager.port
        server_ip, server_port = self.peer.address
        msg.nVersion = HANDSHAKE_VERSION
        msg.addrTo.ip = server_ip
        msg.addrTo.port = server_port
        msg.addrFrom.ip = local_ip
        msg.addrFrom.port = local_port
        msg.nNonce = generate_nonce()
        return msg

    def update(self):
        """Keep the peer connection updated."""
        while True:
            logger.info('Running update thread for peer {}'.format(self.peer))

            if not self.connection_manager.has_connection(self.peer.address):
                return

            # Disconnect from peer if unhealthy
            if self.peer.has_handshake_timeout():
                logger.info('Closing peer because of handshake timeout {}'.format(self.peer))
                self.peer.close()
            if self.peer.has_inactive_timeout():
                logger.info('Closing peer because of last message timeout {}'.format(self.peer))
                self.peer.close()
            if self.peer.has_ping_timeout():
                logger.info('Closing peer because of ping timeout {}'.format(self.peer))
                self.peer.close()

            # Check if it's time to send a ping.
            if self.peer.is_time_for_ping():
                self.initiate_ping()

            # Sleep
            time.sleep(UPDATE_TIME_INTERVAL)
