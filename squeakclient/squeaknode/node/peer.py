import logging
import time
from io import BytesIO

from bitcoin.core.serialize import SerializationTruncationError
from bitcoin.net import CAddress
from squeak.messages import MsgSerializable


MAX_MESSAGE_LEN = 1048576
SOCKET_READ_LEN = 1024
HANDSHAKE_TIMEOUT = 30
LAST_MESSAGE_TIMEOUT = 600
PING_TIMEOUT = 10
PING_INTERVAL = 60


logger = logging.getLogger(__name__)


class Peer(object):
    """Maintains the internal state of a peer connection.
    """

    def __init__(self, peer_socket, address, outgoing=False):
        time_now = int(time.time())
        self._peer_socket = peer_socket
        self._address = address
        self._outgoing = outgoing
        self._connect_time = time_now
        self._local_version = None
        self._remote_version = None
        self._handshake_complete = False
        self._message_decoder = MessageDecoder()
        self._last_msg_revc_time = time_now
        self._last_sent_ping_nonce = None
        self._last_sent_ping_time = None
        self._last_recv_ping_time = None

    @property
    def nVersion(self):
        remote_version = self._remote_version
        if remote_version:
            return remote_version.nVersion

    @property
    def address(self):
        return self._address

    @property
    def address_string(self):
        ip, port = self._address
        return '{}:{}'.format(ip, port)

    @property
    def caddress(self):
        ip, port = self._address
        caddress = CAddress()
        caddress.nTime = self.connect_time
        caddress.ip = ip
        caddress.port = port
        return caddress

    @property
    def outgoing(self):
        return self._outgoing

    @property
    def connect_time(self):
        return self._connect_time

    @property
    def local_version(self):
        return self._local_version

    def set_local_version(self, version):
        self._local_version = version

    @property
    def remote_version(self):
        return self._remote_version

    def set_remote_version(self, version):
        self._remote_version = version

    @property
    def handshake_complete(self):
        return self._handshake_complete

    def set_handshake_complete(self, handshake_complete):
        self._handshake_complete = handshake_complete

    @property
    def last_msg_revc_time(self):
        return self._last_msg_revc_time

    @property
    def last_sent_ping_time(self):
        return self._last_sent_ping_time

    def set_last_sent_ping(self, nonce, timestamp=None):
        timestamp = timestamp or time.time()
        self._last_sent_ping_nonce = nonce
        self._last_sent_ping_time = time.time()

    @property
    def last_recv_ping_time(self):
        return self._last_recv_ping_time

    def set_last_recv_ping(self, timestamp=None):
        timestamp = timestamp or time.time()
        self._last_recv_ping_time = timestamp

    def handle_recv_data(self, handle_msg_fn):
        recv_data = self._peer_socket.recv(SOCKET_READ_LEN)
        if not recv_data:
            raise Exception('Peer disconnected')

        for msg in self._message_decoder.process_recv_data(recv_data):
            self._last_msg_revc_time = time.time()
            handle_msg_fn(msg, self)

    def close(self):
        logger.info("closing peer socket: {}".format(self._peer_socket))
        if self._peer_socket:
            self._peer_socket.close()

    def send_msg(self, msg):
        logger.debug('Sending message of type {}'.format(msg.command))
        data = msg.to_bytes()
        self._peer_socket.send(data)

    def has_handshake_timeout(self):
        """Return True if the handshake has timed out."""
        if self._handshake_complete:
            return False
        return time.time() - self._connect_time > HANDSHAKE_TIMEOUT

    def has_inactive_timeout(self):
        """Return True if the last message received time has timed out."""
        if self._last_msg_revc_time is None:
            return False
        return time.time() - self._last_msg_revc_time > LAST_MESSAGE_TIMEOUT

    def has_ping_timeout(self):
        """Return True if the ping has timed out."""
        last_sent_ping_nonce = self._last_sent_ping_nonce
        last_sent_ping_time = self._last_sent_ping_time
        if last_sent_ping_nonce is None:
            return False
        if last_sent_ping_time is None:
            return False
        return time.time() - last_sent_ping_time > PING_TIMEOUT

    def is_time_for_ping(self):
        """Return True if a ping message needs to be sent."""
        last_sent_ping_time = self._last_sent_ping_time
        if last_sent_ping_time is None:
            return True
        return time.time() - last_sent_ping_time > PING_INTERVAL

    def handle_pong(self, pong):
        if pong.nonce == self._last_sent_ping_nonce:
            self._last_sent_ping_nonce = None

    def __repr__(self):
        return "Peer(%s)" % (self.address_string)


class MessageDecoder:
    """Handles the incoming binary data from a peer and buffers and decodes.
    """

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
