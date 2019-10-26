import time
import threading
import logging

from squeakclient.squeaknode.node.peer_message_handler import PeerMessageHandler
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
        peer_listener = PeerListener(peer, self.connection_manager, self.peer_manager, self.squeaks_access)
        peer_handshaker = PeerHandshaker(peer, self.connection_manager, self.peer_manager, self.squeaks_access)

        listen_thread = threading.Thread(
            target=peer_listener.listen_msgs,
        )
        handshaker_thread = threading.Thread(
            target=peer_handshaker.hanshake,
        )
        # update_thread = threading.Thread(
        #     target=peer_message_handler.peer_controller.update,
        # )

        logger.debug('Peer thread starting... {}'.format(peer))
        try:
            listen_thread.start()
            # update_thread.start()
            logger.debug('Peer listen thread started... {}'.format(peer))

            # Do the handshake.
            handshaker_thread.start()

            # Wait for the listen thread to finish
            listen_thread.join()
            logger.debug('Peer listen thread stopped... {}'.format(peer))

            # Close and remove the peer before stopping.
            peer.close()
        finally:
            self.connection_manager.remove_peer(peer)
            logger.debug('Peer connection removed... {}'.format(peer))


class PeerListener(PeerMessageHandler):
    """Handles receiving messages from a peer.
    """

    def __init__(self, peer, connection_manager, peer_manager, squeaks_access) -> None:
        super().__init__(peer, connection_manager, peer_manager, squeaks_access)

    def listen_msgs(self):
        while True:
            try:
                self.handle_msgs()
            except Exception as e:
                logger.exception('Error in handle_msgs: {}'.format(e))
                return


class PeerHandshaker(PeerController):
    """Handles the peer handshake.
    """

    def __init__(self, peer, connection_manager, peer_manager, squeaks_access) -> None:
        super().__init__(peer, connection_manager, peer_manager, squeaks_access)

    def hanshake(self):
        # Initiate handshake with the peer if the connection is outgoing.
        if self.peer.outgoing:
            self.initiate_handshake()

        # Sleep for 10 seconds.
        time.sleep(10)

        # Disconnect from peer if handshake is not complete.
        if self.peer.has_handshake_timeout():
            logger.info('Closing peer because of handshake timeout {}'.format(self.peer))
            self.peer.close()


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
