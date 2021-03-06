import logging

from squeakclient.squeaknode.node.connection import Connection
from squeakclient.squeaknode.node.peer import Peer


logger = logging.getLogger(__name__)


class PeerHandler():
    """Handles new peer connection.
    """

    def __init__(self, node):
        super().__init__()
        self.node = node

    def start(self, peer_socket, address, outgoing):
        """Handles all sending and receiving of messages for the given peer.

        This method blocks until the peer connection has stopped.
        """
        logger.debug('Setting up controller for peer address {} ...'.format(address))
        with Peer(peer_socket, address, outgoing) as p:
            with Connection(p, self.node):
                p.stopped.wait()
        logger.debug('Stopped controller for peer address {}.'.format(address))


# class PeerListener(PeerMessageHandler):
#     """Handles receiving messages from a peer.
#     """

#     def __init__(self, peer_message_handler) -> None:
#         self.peer_message_handler = peer_message_handler

#     def listen_msgs(self):
#         while True:
#             try:
#                 self.peer_message_handler.handle_msgs()
#             except Exception as e:
#                 logger.exception('Error in handle_msgs: {}'.format(e))
#                 return


# class PeerHandshaker(Connection):
#     """Handles the peer handshake.
#     """

#     def __init__(self, peer, connection_manager, peer_server, squeaks_access) -> None:
#         super().__init__(peer, connection_manager, peer_server, squeaks_access)

#     def hanshake(self):
#         # Initiate handshake with the peer if the connection is outgoing.
#         if self.peer.outgoing:
#             self.initiate_handshake()

#         # Sleep for 10 seconds.
#         time.sleep(10)

#         # Disconnect from peer if handshake is not complete.
#         if self.peer.has_handshake_timeout():
#             logger.info('Closing peer because of handshake timeout {}'.format(self.peer))
#             self.peer.close()


# class PeerPingChecker():
#     """Handles receiving messages from a peer.
#     """

#     def __init__(self, peer_message_handler) -> None:
#         super().__init__()
#         self.peer_message_handler = peer_message_handler

#     def handle_msgs(self):
#         while True:
#             try:
#                 self.peer_message_handler.handle_msgs()
#             except Exception as e:
#                 logger.exception('Error in handle_msgs: {}'.format(e))
#                 return
