import logging
import time
from io import BytesIO

from bitcoin.core.serialize import SerializationTruncationError
from bitcoin.net import CAddress
from squeak.messages import msg_ping
from squeak.messages import MsgSerializable

from squeakclient.squeaknode.util import generate_nonce


MAX_MESSAGE_LEN = 1048576
SOCKET_READ_LEN = 1024
HANDSHAKE_TIMEOUT = 30
LAST_MESSAGE_TIMEOUT = 600
PING_TIMEOUT = 10
PING_INTERVAL = 60


logger = logging.getLogger(__name__)


class Peer(object):

    def __init__(self, peer_socket, address, outgoing=False):
        time_now = int(time.time())
        self.peer_socket = peer_socket
        self.address = address
        self.outgoing = outgoing
        self.connect_time = time_now
        self.my_version = None
        self.version = None
        self.sent_version = False
        self.handshake_complete = False
        self.message_decoder = MessageDecoder()
        self.last_msg_revc_time = time_now
        self.sent_ping = None
        self.last_ping_time = time_now

    @property
    def nVersion(self):
        if self.version:
            return self.version.nVersion

    @property
    def address_string(self):
        ip, port = self.address
        return '{}:{}'.format(ip, port)

    @property
    def caddress(self):
        ip, port = self.address
        caddress = CAddress()
        caddress.nTime = self.connect_time
        caddress.ip = ip
        caddress.port = port
        return caddress

    def handle_recv_data(self, handle_msg_fn):
        recv_data = self.peer_socket.recv(SOCKET_READ_LEN)
        if not recv_data:
            raise Exception('Peer disconnected')

        for msg in self.message_decoder.process_recv_data(recv_data):
            self.last_msg_revc_time = time.time()
            handle_msg_fn(msg, self)

    def close(self):
        logger.info("closing peer socket: {}".format(self.peer_socket))
        if self.peer_socket:
            self.peer_socket.close()

    def send_msg(self, msg):
        logger.debug('Sending message of type {}'.format(msg.command))
        data = msg.to_bytes()
        self.peer_socket.send(data)

    def health_check(self):
        # Disconnect peers without handshake
        if not self.handshake_complete:
            if time.time() - self.connect_time > HANDSHAKE_TIMEOUT:
                logger.info('Closing peer because of handshake timeout {}'.format(self))
                self.close()
                return

        # Check for inactive peers
        if time.time() - self.last_msg_revc_time > LAST_MESSAGE_TIMEOUT:
            logger.info('Closing peer because of last message timeout {}'.format(self))
            self.close()
            return

        # Check for ping timeouts
        sent_ping = self.sent_ping
        if sent_ping:
            (nonce, sent_time) = sent_ping
            if time.time() - sent_time > PING_TIMEOUT:
                logger.info('Closing peer because of ping timeout {}'.format(self))
                self.close()
                return

        # Check for pings that should be sent
        if time.time() - self.last_ping_time > PING_INTERVAL:
            self.send_ping()

    def send_ping(self):
        nonce = generate_nonce()
        sent_time = time.time()
        ping = msg_ping()
        ping.nonce = nonce
        self.send_msg(ping)
        self.sent_ping = (nonce, sent_time)
        self.last_ping_time = sent_time

    def handle_pong(self, pong):
        sent_ping = self.sent_ping
        if sent_ping:
            (nonce, sent_time) = sent_ping
            if pong.nonce == nonce:
                self.sent_ping = None

    def __repr__(self):
        return "Peer(%s)" % (self.address_string)


class MessageDecoder:

    def __init__(self):
        self.recv_data_buffer = BytesIO()

    def process_recv_data(self, recv_data):
        data = self.read_data_buffer() + recv_data
        try:
            while data:
                self.set_data_buffer(data)
                msg = MsgSerializable.stream_deserialize(self.recv_data_buffer)
                if msg is None:
                    raise Exception('Invalid data')
                else:
                    self.last_msg_revc_time = time.time()
                    yield msg
                    data = self.read_data_buffer()
        except SerializationTruncationError:
            self.set_data_buffer(data)

    def read_data_buffer(self):
        return self.recv_data_buffer.read()

    def set_data_buffer(self, data):
        if len(data) > MAX_MESSAGE_LEN:
            raise Exception('Message size too large')
        self.recv_data_buffer = BytesIO(data)
