import threading
import logging

from squeakclient.squeaknode.node.peer_message_handler import PeerMessageHandler


logger = logging.getLogger(__name__)


HANDSHAKE_TIMEOUT = 30
UPDATE_TIME_INTERVAL = 10
HANDSHAKE_VERSION = 70002


class PeerController():
    """Commands for interacting with remote peer.
    """

    def __init__(self, peer, node, connection_manager):
        super().__init__()
        self.peer = peer
        self.node = node
        self.connection_manager = connection_manager

        peer_listener = PeerListener(self.peer, self.node)
        peer_handshaker = PeerHandshaker(self.peer, self.node)

        self.message_listener_thread = threading.Thread(
            target=peer_listener.start,
        )
        self.handshaker_thread = threading.Thread(
            target=peer_handshaker.start,
        )
        # update_thread = threading.Thread(
        #     target=peer_message_handler.peer_controller.update,
        # )

    def start(self):
        logger.debug('Peer thread starting... {}'.format(self.peer))
        try:
            self.message_listener_thread.start()
            logger.debug('Peer message handler thread started... {}'.format(self.peer))
            self.handshaker_thread.start()
            logger.debug('Peer handshaker thread started... {}'.format(self.peer))

            # Wait for the listen thread to finish
            self.message_listener_thread.join()
            logger.debug('Peer message handler thread stopped... {}'.format(self.peer))

            # Close and remove the peer before stopping.
            self.peer.close()
        finally:
            logger.debug('Peer controller stopped... {}'.format(self.peer))

    def __enter__(self):
        self.connection_manager.add_peer(self.peer)
        logger.debug('Peer connection added... {}'.format(self.peer))
        return self

    def __exit__(self, *exc):
        self.connection_manager.remove_peer(self.peer)
        logger.debug('Peer connection removed... {}'.format(self.peer))


class PeerListener:
    """Handles receiving messages from a peer.
    """

    def __init__(self, peer, node):
        self.peer = peer
        self.node = node
        self.peer_message_handler = PeerMessageHandler(peer, node)

    def start(self):
        while True:
            try:
                self.peer_message_handler.handle_msgs()
            except Exception as e:
                logger.exception('Error in handle_msgs: {}'.format(e))
                return


class PeerHandshaker:
    """Handles receiving messages from a peer.
    """

    def __init__(self, peer, node):
        self.peer = peer
        self.node = node

    def start(self):
        # Start the handshake.
        logger.debug('Starting handshake with {}'.format(self.peer))
        if self.peer.outgoing:
            self.peer.send_version(self.node)

        # Wait for the handshake to complete.
        handshake_result = self.peer.handshake_complete.wait(HANDSHAKE_TIMEOUT)
        if not handshake_result:
            logger.debug('Handshake failure')
            self.peer.stop()
