import threading
import logging

from squeakclient.squeaknode.node.peer import Peer
from squeakclient.squeaknode.node.peer_message_handler import PeerMessageHandler


logger = logging.getLogger(__name__)


HANDSHAKE_TIMEOUT = 30
UPDATE_TIME_INTERVAL = 10
HANDSHAKE_VERSION = 70002


class PeerController():
    """Commands for interacting with remote peer.
    """

    def __init__(self, peer: Peer, connection_manager, peer_manager, squeaks_access) -> None:
        super().__init__()
        self.peer = peer
        self.connection_manager = connection_manager

        self.peer_message_handler = PeerMessageHandler(peer, connection_manager, peer_manager, squeaks_access)
        self.peer_listener = PeerListener(self.peer_message_handler)
        self.peer_handshaker = PeerHandshaker(self.peer, self.peer_message_handler)
        # peer_handshaker = PeerHandshaker(peer, self.connection_manager, self.peer_manager, self.squeaks_access)

        self.listen_thread = threading.Thread(
            target=self.peer_listener.listen_msgs,
        )
        self.handshaker_thread = threading.Thread(
            target=self.peer_handshaker.start,
        )
        # update_thread = threading.Thread(
        #     target=peer_message_handler.peer_controller.update,
        # )

    def start(self):
        logger.debug('Peer thread starting... {}'.format(self.peer))
        try:
            self.listen_thread.start()
            self.peer_handshaker.start()
            # update_thread.start()
            logger.debug('Peer listen thread started... {}'.format(self.peer))
            logger.debug('Peer handshaker thread started... {}'.format(self.peer))

            # # Do the handshake.
            # handshaker_thread.start()
            # peer_message_handler.initiate_handshake()

            # Wait for the listen thread to finish
            self.listen_thread.join()
            logger.debug('Peer listen thread stopped... {}'.format(self.peer))

            # Close and remove the peer before stopping.
            self.peer.close()
        finally:
            self.connection_manager.remove_peer(self.peer)
            logger.debug('Peer connection removed... {}'.format(self.peer))


class PeerListener:
    """Handles receiving messages from a peer.
    """

    def __init__(self, peer_message_handler) -> None:
        super().__init__()
        self.peer_message_handler = peer_message_handler

    def listen_msgs(self):
        while True:
            try:
                self.peer_message_handler.handle_msgs()
            except Exception as e:
                logger.exception('Error in handle_msgs: {}'.format(e))
                return


class PeerHandshaker:
    """Handles receiving messages from a peer.
    """

    def __init__(self, peer, peer_message_handler) -> None:
        self.peer = peer
        self.peer_message_handler = peer_message_handler

    def start(self):
        # Start the handshake.
        if self.peer.outgoing:
            self.peer_message_handler.initiate_handshake()

        # Wait for the handshake to complete.
        handshake_result = self.peer._handshake_complete.wait(HANDSHAKE_TIMEOUT)
        if handshake_result:
            logger.debug('Handshake success')
        else:
            logger.debug('Handshake failure')
