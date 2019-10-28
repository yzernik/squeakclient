import logging

from squeak.messages import msg_version

from squeakclient.squeaknode.util import generate_nonce

from squeakclient.squeaknode.node.peer import Peer


logger = logging.getLogger(__name__)


HANDSHAKE_VERSION = 70002


class PeerCommunicator:
    """Handles communication with a peer.
    """

    def __init__(self, peer: Peer, peer_manager) -> None:
        self.peer = peer
        self.peer_manager = peer_manager

    def send_msg(self, msg):
        """Send a message to the peer."""
        self.peer.send_msg(msg)

    def version_pkt(self):
        """Get the version message for this peer."""
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
