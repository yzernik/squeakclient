import logging

from squeakclient.squeaknode.node.peer_controller import PeerController


logger = logging.getLogger(__name__)


HANDSHAKE_TIMEOUT = 30
LAST_MESSAGE_TIMEOUT = 600
PING_TIMEOUT = 10
PING_INTERVAL = 60
HANDSHAKE_VERSION = 70002


class PeerHandler():
    """Handles new peer connection.
    """

    def __init__(self, connection_manager, peer_manager, squeaks_access) -> None:
        super().__init__()
        self.connection_manager = connection_manager
        self.peer_manager = peer_manager
        self.squeaks_access = squeaks_access

    def start(self, peer):
        """Handles all sending and receiving of messages for the given peer.

        This method blocks until the peer connection has stopped.
        """
        logger.debug('Setting up controller for peer {} ...'.format(peer))
        peer_controller = PeerController(peer, self.connection_manager, self.peer_manager, self.squeaks_access)
        with peer_controller as pc:
            pc.start()
        logger.debug('Stopped controller for peer {}.'.format(peer))


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


# class PeerHandshaker(PeerController):
#     """Handles the peer handshake.
#     """

#     def __init__(self, peer, connection_manager, peer_manager, squeaks_access) -> None:
#         super().__init__(peer, connection_manager, peer_manager, squeaks_access)

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
