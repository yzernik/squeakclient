import threading
import logging

from squeakclient.squeaknode.node.peer_message_handler import PeerMessageHandler


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
        peer_message_hander = PeerMessageHandler(peer, self.connection_manager, self.peer_manager, self.squeaks_access)

        listen_thread = threading.Thread(
            target=peer_message_hander.handle_msgs,
        )
        update_thread = threading.Thread(
            target=peer_message_hander.peer_controller.update,
        )

        logger.debug('Peer thread starting... {}'.format(peer))
        if self.connection_manager.add_peer(peer):
            logger.debug('Peer connection added... {}'.format(peer))
            listen_thread.start()
            update_thread.start()
            logger.debug('Peer listen thread started... {}'.format(peer))

            # Initiate handshake with the peer.
            peer_message_hander.peer_controller.initiate_handshake()

            # Wait for the listen thread to finish
            listen_thread.join()
            logger.debug('Peer listen thread stopped... {}'.format(peer))

            # Close and remove the peer before stopping.
            peer.close()
            self.connection_manager.remove_peer(peer)
            logger.debug('Peer connection removed... {}'.format(peer))
