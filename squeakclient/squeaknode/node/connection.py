import logging

from squeakclient.squeaknode.util import generate_nonce

from squeak.messages import msg_version
from squeak.messages import msg_verack

logger = logging.getLogger(__name__)


HANDSHAKE_TIMEOUT = 30
UPDATE_TIME_INTERVAL = 10
HANDSHAKE_VERSION = 70002


class Connection():
    """Commands for interacting with remote peer.
    """

    def __init__(self, peer, node):
        super().__init__()
        self.peer = peer
        self.node = node

    def handshake(self):
        if self.peer.outgoing:
            local_version = self.version_pkt()
            self.peer.local_version = local_version
            self.peer.send_msg(local_version)
            verack = self.peer.recv_msg()
            if not isinstance(verack, msg_verack):
                raise Exception('Wrong message type for verack response.')

        remote_version = self.peer.recv_msg()
        if not isinstance(remote_version, msg_version):
            raise Exception('Wrong message type for version message.')
        if self._is_duplicate_nonce(remote_version.nNonce):
            raise Exception('Remote nonce is duplicate of local nonce.')
        self.peer.remote_version = remote_version
        verack = msg_verack()
        self.peer.send_msg(verack)

        if not self.peer.outgoing:
            local_version = self.version_pkt()
            self.peer.local_version = local_version
            self.peer.send_msg(local_version)
            verack = self.peer.recv_msg()
            if not isinstance(verack, msg_verack):
                raise Exception('Wrong message type for verack response.')

        return

    def version_pkt(self):
        """Get the version message for this peer."""
        msg = msg_version()
        local_ip, local_port = self.node.address
        server_ip, server_port = self.peer.address
        msg.nVersion = HANDSHAKE_VERSION
        msg.addrTo.ip = server_ip
        msg.addrTo.port = server_port
        msg.addrFrom.ip = local_ip
        msg.addrFrom.port = local_port
        msg.nNonce = generate_nonce()
        return msg

    def __enter__(self):
        logger.debug('Starting handshake connection with peer ... {}'.format(self.peer))
        self.node.connection_manager.add_peer(self.peer)
        self.handshake()
        logger.debug('Peer connection added... {}'.format(self.peer))
        return self

    def __exit__(self, *exc):
        self.node.connection_manager.remove_peer(self.peer)
        logger.debug('Peer connection removed... {}'.format(self.peer))

    def _is_duplicate_nonce(self, nonce):
        for peer in self.node.connection_manager.peers:
            if peer.local_version:
                if nonce == peer.local_version.nNonce:
                    return True
        return False


# class PeerListener:
#     """Handles receiving messages from a peer.
#     """

#     def __init__(self, peer, node):
#         self.peer = peer
#         self.node = node
#         self.peer_message_handler = PeerMessageHandler(peer, node)

#     def start(self):
#         while True:
#             try:
#                 self.peer_message_handler.handle_msgs()
#             except Exception as e:
#                 logger.exception('Error in handle_msgs: {}'.format(e))
#                 return
