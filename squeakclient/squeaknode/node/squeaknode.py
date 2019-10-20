import logging

from squeak.messages import msg_addr
from squeak.messages import msg_getaddr
from squeak.messages import msg_getdata
from squeak.messages import msg_inv
from squeak.messages import msg_notfound
from squeak.messages import msg_pong
from squeak.messages import msg_squeak
from squeak.net import CInv

from squeakclient.squeaknode.node.access import PeersAccess
from squeakclient.squeaknode.node.access import SqueaksAccess
from squeakclient.squeaknode.node.peernode import PeerMessageHandler


logger = logging.getLogger(__name__)


class ClientPeerMessageHandler(PeerMessageHandler):
    """Handles incoming messages from peers.
    """

    def __init__(self, peers_access: PeersAccess, squeaks_access: SqueaksAccess) -> None:
        super().__init__()
        self.peers_access = peers_access
        self.squeaks_access = squeaks_access

    def initialize_peer(self, peer):
        logger.debug('Initializing peer connection with {}'.format(peer))
        peer.send_ping()
        if peer.outgoing:
            self.peers_access.send_msg(peer, msg_getaddr())

    def handle_peer_message(self, msg, peer):
        """Handle messages from a peer with completed handshake."""
        if msg.command == b'ping':
            self.handle_ping(msg, peer)
        if msg.command == b'pong':
            self.handle_pong(msg, peer)
        if msg.command == b'addr':
            self.handle_addr(msg, peer)
        if msg.command == b'getaddr':
            self.handle_getaddr(msg, peer)
        if msg.command == b'inv':
            self.handle_inv(msg, peer)
        if msg.command == b'getsqueaks':
            self.handle_getsqueaks(msg, peer)
        if msg.command == b'squeak':
            self.handle_squeak(msg, peer)
        if msg.command == b'getdata':
            self.handle_getdata(msg, peer)
        if msg.command == b'notfound':
            self.handle_notfound(msg, peer)

    def handle_ping(self, msg, peer):
        nonce = msg.nonce
        pong = msg_pong()
        pong.nonce = nonce
        self.peers_access.send_msg(peer, pong)

    def handle_pong(self, msg, peer):
        peer.handle_pong(msg)

    def handle_addr(self, msg, peer):
        for addr in msg.addrs:
            self.peers_access.add_address((addr.ip, addr.port))

    def handle_getaddr(self, msg, peer):
        peers = self.peers_access.get_connected_peers()
        addresses = [peer.caddress for peer in peers
                     if peer.outgoing]
        addr_msg = msg_addr(addrs=addresses)
        self.peers_access.send_msg(peer, addr_msg)

    def handle_inv(self, msg, peer):
        invs = msg.inv
        saved_hashes = set(self.squeaks_access.get_squeak_hashes())
        received_hashes = set([inv.hash
                               for inv in invs
                               if inv.type == 1])
        new_hashes = received_hashes - saved_hashes

        new_invs = [CInv(type=1, hash=hash)
                    for hash in new_hashes]
        getdata_msg = msg_getdata(inv=new_invs)
        self.peers_access.send_msg(peer, getdata_msg)

    def handle_getdata(self, msg, peer):
        invs = msg.inv
        not_found = []
        for inv in invs:
            if inv.type == 1:
                squeak = self.squeaks_access.get_squeak(inv.hash)
                if squeak:
                    squeak_msg = msg_squeak(squeak=squeak)
                    self.peers_access.send_msg(peer, squeak_msg)
                else:
                    not_found.append(inv)
        notfound_msg = msg_notfound(inv=not_found)
        self.peers_access.send_msg(peer, notfound_msg)

    def handle_notfound(self, msg, peer):
        pass

    def handle_getsqueaks(self, msg, peer):
        locator = msg.locator
        squeaks = self.squeaks_access.get_squeaks_by_locator(locator)
        invs = [CInv(type=1, hash=squeak.GetHash())
                for squeak in squeaks]
        inv_msg = msg_inv(inv=invs)
        self.peers_access.send_msg(peer, inv_msg)

    def handle_squeak(self, msg, peer):
        # TODO: If squeak is interesting, respond with getoffer msg.
        squeak = msg.squeak
        self.squeaks_access.add_squeak(squeak)

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
