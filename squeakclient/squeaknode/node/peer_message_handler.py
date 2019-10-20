import logging

from squeak.messages import msg_addr
from squeak.messages import msg_getaddr
from squeak.messages import msg_getdata
from squeak.messages import msg_inv
from squeak.messages import msg_notfound
from squeak.messages import msg_pong
from squeak.messages import msg_squeak
from squeak.messages import msg_verack
from squeak.messages import msg_version
from squeak.net import CInv

from squeakclient.squeaknode.node.access import PeersAccess
from squeakclient.squeaknode.node.access import SqueaksAccess
from squeakclient.squeaknode.util import generate_nonce


logger = logging.getLogger(__name__)


HANDSHAKE_TIMEOUT = 30
LAST_MESSAGE_TIMEOUT = 600
PING_TIMEOUT = 10
PING_INTERVAL = 60
HANDSHAKE_VERSION = 70002


class PeerMessageHandler():
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

    def version_pkt(self, peer):
        msg = msg_version()
        local_ip, local_port = self.peers_access.get_local_ip_port()
        server_ip, server_port = peer.address
        msg.nVersion = HANDSHAKE_VERSION
        msg.addrTo.ip = server_ip
        msg.addrTo.port = server_port
        msg.addrFrom.ip = local_ip
        msg.addrFrom.port = local_port
        msg.nNonce = generate_nonce()
        return msg

    def initialize_connection(self, peer):
        logger.debug('Initializing connection with {}'.format(peer))
        self.initialize_peer(peer)

    def handle_peer_message(self, msg, peer):
        """Handle messages from a peer with completed handshake."""

        # Only allow version and verack messages before handshake is complete.
        if not peer.handshake_complete and msg.command not in [
                b'version',
                b'verack',
        ]:
            raise Exception('Received non-handshake message from un-handshaked peer.')

        if msg.command == b'version':
            self.handle_version(msg, peer)
        if msg.command == b'verack':
            self.handle_verack(msg, peer)
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

    def handle_version(self, msg, peer):
        logger.debug('Handling version message from peer {}'.format(peer))
        if msg.nNonce in self.peers_access.get_peer_nonces():
            logger.debug('Closing connection because of matching nonce with peer {}'.format(peer))
            peer.close()
            return

        peer.version = msg
        if not peer.sent_version:
            version = self.version_pkt(peer)
            peer.my_version = version
            self.peers_access.send_msg(peer, version)
            peer.sent_version = True
        self.peers_access.send_msg(peer, msg_verack())

    def handle_verack(self, msg, peer):
        logger.debug('Handling verack message from peer {}'.format(peer))
        if peer.version is not None and peer.sent_version:
            peer.handshake_complete = True
            # self.on_peers_changed()  # TODO: call on_peers_changed inside set_handshake_complete method.
            logger.debug('Handshake complete with {}'.format(peer))
            self.initialize_connection(peer)

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
