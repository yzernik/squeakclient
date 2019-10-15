import logging

from squeak.messages import msg_verack
from squeak.messages import msg_version

from squeakclient.squeaknode.node.peernode import PeerNode
from squeakclient.squeaknode.util import generate_nonce


HANDSHAKE_TIMEOUT = 30
LAST_MESSAGE_TIMEOUT = 600
PING_TIMEOUT = 10
PING_INTERVAL = 60
HANDSHAKE_VERSION = 70002


logger = logging.getLogger(__name__)


class HandshakeNode(PeerNode):
    """Handles handshakes with connected peers.
    """

    def __init__(self):
        super().__init__()

    def on_connect(self, peer):
        logger.debug('Starting handshake with {}'.format(peer))
        version = self.version_pkt(peer)
        peer.my_version = version
        self.send_msg(peer, version)
        peer.sent_version = True

    def handle_msg(self, msg, peer):
        """Main message handler.
        """
        logger.debug('Received msg {} from {}'.format(msg, peer))
        if msg.command == b'version':
            self.handle_version(msg, peer)
        elif msg.command == b'verack':
            self.handle_verack(msg, peer)
        elif peer.handshake_complete:
            self.peer_msg_handler.handle_peer_message(msg, peer)

    def handle_version(self, msg, peer):
        if msg.nNonce in self.get_peer_nonces():
            logger.debug('Closing connection because of matching nonce with peer {}'.format(peer))
            peer.close()
            return

        peer.version = msg
        if not peer.sent_version:
            version = self.version_pkt(peer)
            peer.my_version = version
            self.send_msg(peer, version)
            peer.sent_version = True
        self.send_msg(peer, msg_verack())

    def handle_verack(self, msg, peer):
        if peer.version is not None and peer.sent_version:
            peer.handshake_complete = True
            self.on_peers_changed()
            logger.debug('Handshake complete with {}'.format(peer))
            self.initialize_connection(peer)

    def initialize_connection(self, peer):
        logger.debug('Initializing connection with {}'.format(peer))
        self.peer_msg_handler.initialize_peer(peer)

    def version_pkt(self, peer):
        msg = msg_version()
        server_ip, server_port = peer.address
        msg.nVersion = HANDSHAKE_VERSION
        msg.addrTo.ip = server_ip
        msg.addrTo.port = server_port
        msg.addrFrom.ip = self.ip
        msg.addrFrom.port = self.port
        msg.nNonce = generate_nonce()
        return msg

    def get_peer_nonces(self):
        peers = list(self.peers.values())
        return [peer.my_version.nNonce if peer.my_version else None
                for peer in peers]
