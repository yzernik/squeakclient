import logging

from squeak.messages import msg_pong
from squeak.messages import msg_squeak

from squeakclient.squeaknode.core.stores.storage import Storage
from squeakclient.squeaknode.node.handshakenode import HandshakeNode


logger = logging.getLogger(__name__)


class SqueakNode(HandshakeNode):
    """Network node that implements the network protocol.
    """

    def __init__(self, storage: Storage) -> None:
        super().__init__()
        self.storage = storage

    def handle_connected_peer_msg(self, msg, peer):
        """Handle messages from a peer with completed handshake."""
        logger.debug('Peer-connected msg {} from {}'.format(msg.command, peer))
        if msg.command == b'ping':
            self.handle_ping(msg, peer)
        if msg.command == b'pong':
            self.handle_pong(msg, peer)
        if msg.command == b'addr':
            self.handle_addr(msg, peer)
        if msg.command == b'inv':
            self.handle_inv(msg, peer)
        if msg.command == b'getsqueaks':
            self.handle_getsqueaks(msg, peer)
        if msg.command == b'squeak':
            self.handle_squeak(msg, peer)

    def handle_ping(self, msg, peer):
        nonce = msg.nonce
        pong = msg_pong()
        pong.nonce = nonce
        self.send_msg(peer, pong)

    def handle_pong(self, msg, peer):
        peer.handle_pong(msg)

    def handle_addr(self, msg, peer):
        for addr in msg.addrs:
            self.add_address((addr.ip, addr.port))

    def handle_inv(self, msg, peer):
        # TODO: Respond with getdata msg with the list of inv_vects.
        pass

    def handle_getdata(self, msg, peer):
        # TODO: For each inv_vect, respond with squeak msg.
        pass

    def handle_notfound(self, msg, peer):
        pass

    def handle_getsqueaks(self, msg, peer):
        locator = msg.locator
        squeaks = self.storage.get_squeak_store().get_squeaks_by_locator(locator)
        logger.info('Found squeaks: {} in response to getsqueaks from {}'.format(squeaks, peer))
        for squeak in squeaks:
            squeak_msg = msg_squeak(squeak=squeak)
            self.send_msg(peer, squeak_msg)

    def handle_squeak(self, msg, peer):
        # TODO: If squeak is interesting, respond with getoffer msg.
        squeak = msg.squeak
        logger.info('Received squeak {} from peer {}'.format(squeak, peer))
        self.add_squeak(squeak)

    def handle_getoffer(self, msg, peer):
        # Respond with offer msg.
        pass

    def handle_offer(self, msg, peer):
        # Respond with getinvoice.
        pass

    def handle_getinvoice(self, msg, peer):
        # Respond with invoice.
        pass

    def handle_invoice(self, msg, peer):
        # Pay the invoice, and then respond with getfulfill.
        pass

    def handle_getfulfill(self, msg, peer):
        # Check if invoice is paid, and then respond with fulfill.
        pass

    def handle_fulfill(self, msg, peer):
        # Decrypt the squeak content, and save it in squeak store.
        pass
