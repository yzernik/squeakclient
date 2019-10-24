import logging

from squeak.messages import msg_addr
from squeak.messages import msg_getaddr
from squeak.messages import msg_getdata
from squeak.messages import msg_inv
from squeak.messages import msg_notfound
from squeak.messages import msg_ping
from squeak.messages import msg_pong
from squeak.messages import msg_squeak
from squeak.messages import msg_verack
from squeak.messages import msg_version
from squeak.net import CInv

from squeakclient.squeaknode.util import generate_nonce
from squeakclient.squeaknode.node.peer import Peer


logger = logging.getLogger(__name__)


HANDSHAKE_TIMEOUT = 30
LAST_MESSAGE_TIMEOUT = 600
PING_TIMEOUT = 10
PING_INTERVAL = 60
HANDSHAKE_VERSION = 70002


class PeerMessageHandler():
    """Handles incoming messages from peers.
    """

    def __init__(self, peer: Peer, peers_access, squeaks_access) -> None:
        super().__init__()
        self.peer = peer
        self.peers_access = peers_access
        self.squeaks_access = squeaks_access

    def initiate_handshake(self):
        """Action to take upon completion of handshake with a peer."""
        logger.debug('Starting handshake with {}'.format(self.peer))
        version = self.version_pkt()
        self.peer.set_local_version(version)
        self.peers_access.send_msg(self.peer, version)

    def initiate_ping(self):
        """Send a ping message and expect a pong response."""
        logger.debug('Sending a ping to {}'.format(self.peer))
        nonce = generate_nonce()
        ping = msg_ping()
        ping.nonce = nonce
        self.peers_access.send_msg(self.peer, ping)
        self.peer.set_last_sent_ping(nonce)

    def version_pkt(self):
        msg = msg_version()
        local_ip, local_port = self.peers_access.get_local_ip_port()
        server_ip, server_port = self.peer.address
        msg.nVersion = HANDSHAKE_VERSION
        msg.addrTo.ip = server_ip
        msg.addrTo.port = server_port
        msg.addrFrom.ip = local_ip
        msg.addrFrom.port = local_port
        msg.nNonce = generate_nonce()
        return msg

    def handle_msgs(self):
        """Handles messages from the peer if there are any available.

        This method blocks when the peer has not sent any messages.
        """
        for msg in self.peer.handle_recv_data():
            self.handle_peer_message(msg)

    def handle_peer_message(self, msg):
        """Handle messages from a peer with completed handshake."""

        # Only allow version and verack messages before handshake is complete.
        if not self.peer.handshake_complete and msg.command not in [
                b'version',
                b'verack',
        ]:
            raise Exception('Received non-handshake message from un-handshaked peer.')

        if msg.command == b'version':
            self.handle_version(msg)
        if msg.command == b'verack':
            self.handle_verack(msg)
        if msg.command == b'ping':
            self.handle_ping(msg)
        if msg.command == b'pong':
            self.handle_pong(msg)
        if msg.command == b'addr':
            self.handle_addr(msg)
        if msg.command == b'getaddr':
            self.handle_getaddr(msg)
        if msg.command == b'inv':
            self.handle_inv(msg)
        if msg.command == b'getsqueaks':
            self.handle_getsqueaks(msg)
        if msg.command == b'squeak':
            self.handle_squeak(msg)
        if msg.command == b'getdata':
            self.handle_getdata(msg)
        if msg.command == b'notfound':
            self.handle_notfound(msg)

    def handle_version(self, msg):
        logger.debug('Handling version message from peer {}'.format(self.peer))
        if msg.nNonce in self.peers_access.get_local_version_nonces():
            logger.debug('Closing connection because of matching nonce with peer {}'.format(self.peer))
            self.peer.close()
            return

        self.peer.set_remote_version(msg)
        if self.peer.local_version is None:
            version = self.version_pkt()
            self.peer.set_local_version(version)
            self.peers_access.send_msg(self.peer, version)
        self.peers_access.send_msg(self.peer, msg_verack())

    def handle_verack(self, msg):
        logger.debug('Handling verack message from peer {}'.format(self.peer))
        if self.peer.remote_version is not None and self.peer.local_version is not None:
            self.peer.set_handshake_complete(True)
            # self.on_peers_changed()  # TODO: call on_peers_changed inside set_handshake_complete method.
            logger.debug('Handshake complete with {}'.format(self.peer))
            self.initiate_ping()
            if self.peer.outgoing:
                self.peers_access.send_msg(self.peer, msg_getaddr())

    def handle_ping(self, msg):
        nonce = msg.nonce
        pong = msg_pong()
        pong.nonce = nonce
        self.peer.set_last_recv_ping()
        self.peers_access.send_msg(self.peer, pong)

    def handle_pong(self, msg):
        self.peer.set_pong_response(msg.nonce)

    def handle_addr(self, msg):
        for addr in msg.addrs:
            self.peers_access.add_address((addr.ip, addr.port))

    def handle_getaddr(self, msg):
        peers = self.peers_access.get_connected_peers()
        addresses = [peer.caddress for peer in peers
                     if peer.outgoing]
        addr_msg = msg_addr(addrs=addresses)
        self.peers_access.send_msg(self.peer, addr_msg)

    def handle_inv(self, msg):
        invs = msg.inv
        saved_hashes = set(self.squeaks_access.get_squeak_hashes())
        received_hashes = set([inv.hash
                               for inv in invs
                               if inv.type == 1])
        new_hashes = received_hashes - saved_hashes

        new_invs = [CInv(type=1, hash=hash)
                    for hash in new_hashes]
        getdata_msg = msg_getdata(inv=new_invs)
        self.peers_access.send_msg(self.peer, getdata_msg)

    def handle_getdata(self, msg):
        invs = msg.inv
        not_found = []
        for inv in invs:
            if inv.type == 1:
                squeak = self.squeaks_access.get_squeak(inv.hash)
                if squeak:
                    squeak_msg = msg_squeak(squeak=squeak)
                    self.peers_access.send_msg(self.peer, squeak_msg)
                else:
                    not_found.append(inv)
        notfound_msg = msg_notfound(inv=not_found)
        self.peers_access.send_msg(self.peer, notfound_msg)

    def handle_notfound(self, msg):
        pass

    def handle_getsqueaks(self, msg):
        locator = msg.locator
        squeaks = self.squeaks_access.get_squeaks_by_locator(locator)
        invs = [CInv(type=1, hash=squeak.GetHash())
                for squeak in squeaks]
        inv_msg = msg_inv(inv=invs)
        self.peers_access.send_msg(self.peer, inv_msg)

    def handle_squeak(self, msg):
        # TODO: If squeak is interesting, respond with getoffer msg.
        squeak = msg.squeak
        self.squeaks_access.add_squeak(squeak)

    def handle_getoffer(self, msg):
        # Respond with offer msg.
        pass

    def handle_offer(self, msg):
        # Respond with getinvoice.
        pass

    def handle_getinvoice(self, msg):
        # Respond with invoice.
        pass

    def handle_invoice(self, msg):
        # Pay the invoice, and then respond with getfulfill.
        pass

    def handle_getfulfill(self, msg):
        # Check if invoice is paid, and then respond with fulfill.
        pass

    def handle_fulfill(self, msg):
        # Decrypt the squeak content, and save it in squeak store.
        pass
