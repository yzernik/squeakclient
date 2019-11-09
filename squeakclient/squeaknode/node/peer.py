import threading
import logging
import time
from io import BytesIO

from bitcoin.core.serialize import SerializationTruncationError
from bitcoin.net import CAddress
from squeak.messages import MsgSerializable
from squeak.messages import msg_version

from squeakclient.squeaknode.util import generate_nonce


MAX_MESSAGE_LEN = 1048576
SOCKET_READ_LEN = 1024
HANDSHAKE_TIMEOUT = 30
LAST_MESSAGE_TIMEOUT = 600
PING_TIMEOUT = 10
PING_INTERVAL = 60
HANDSHAKE_VERSION = 70002


logger = logging.getLogger(__name__)


class Peer(object):
    """Maintains the internal state of a peer connection.
    """

    def __init__(self, peer_socket, address, outgoing=False):
        time_now = int(time.time())
        self._peer_socket = peer_socket
        self._peer_socket_lock = threading.Lock()
        self._address = address
        self._outgoing = outgoing
        self._connect_time = time_now
        self._local_version = None
        self._remote_version = None
        self._message_decoder = MessageDecoder()
        self._last_msg_revc_time = None
        self._last_sent_ping_nonce = None
        self._last_sent_ping_time = None
        self._last_recv_ping_time = None

        self.handshake_complete = threading.Event()
        self.ping_started = threading.Event()
        self.ping_complete = threading.Event()
        self.stopped = threading.Event()

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

    @property
    def remote_version(self):
        return self._remote_version

    @property
    def is_handshake_complete(self):
        return self.handshake_complete.is_set()

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

    def handle_recv_data(self):
        """Read data from the peer socket, and yield messages as they are decoded.

        This method blocks when the socket has no data to read.
        """
        recv_data = self._peer_socket.recv(SOCKET_READ_LEN)
        if not recv_data:
            raise Exception('Peer disconnected')

        for msg in self._message_decoder.process_recv_data(recv_data):
            self._last_msg_revc_time = time.time()
            logger.debug('Received msg {} from {}'.format(msg, self))
            yield msg

    def stop(self):
        logger.info("Stopping peer: {}".format(self))
        self.stopped.set()

    def close(self):
        logger.info("closing peer socket: {}".format(self._peer_socket))
        if self._peer_socket:
            self._peer_socket.close()

    def send_msg(self, msg):
        logger.debug('Sending msg {} to {}'.format(msg, self))
        data = msg.to_bytes()
        with self._peer_socket_lock:
            self._peer_socket.send(data)

    def record_sent_version_msg(self, version_msg):
        # Set the local version.
        if self._local_version is not None:
            raise Exception('Local version is already set.')
        self._local_version = version_msg

    def record_recv_version_msg(self, version_msg):
        # Set the remote version
        if self._remote_version is not None:
            raise Exception('Remote version is already set.')
        self._remote_version = version_msg

    def record_recv_verack_msg(self, verack_msg):
        if self.remote_version is not None and \
           self.local_version is not None:
            logger.debug('Handshake complete with {}'.format(self))
            self.handshake_complete.set()

    def version_pkt(self, node):
        """Get the version message for this peer."""
        msg = msg_version()
        local_ip, local_port = node.address
        server_ip, server_port = self.address
        msg.nVersion = HANDSHAKE_VERSION
        msg.addrTo.ip = server_ip
        msg.addrTo.port = server_port
        msg.addrFrom.ip = local_ip
        msg.addrFrom.port = local_port
        msg.nNonce = generate_nonce()
        return msg

    def send_version(self, node):
        version = self.version_pkt(node)
        self.record_sent_version_msg(version)
        self.send_msg(version)

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
