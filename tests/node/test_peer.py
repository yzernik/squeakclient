from collections import deque

import pytest
from squeak.messages import msg_version

from squeakclient.squeaknode.node.peer import Peer


HANDSHAKE_VERSION = 70002


@pytest.fixture
def address():
    return ('127.0.0.1', 5678)


@pytest.fixture
def peer_socket():
    return MockPeerSocket()


class TestPeer(object):

    def test_send_version(self, address, peer_socket):
        peer = Peer(peer_socket, address)
        version = self.version_pkt(peer)
        peer.send_msg(version)
        data = peer_socket.receive()

        assert data is not None

    def version_pkt(self, peer):
        msg = msg_version()
        server_ip, server_port = peer.address
        msg.nVersion = HANDSHAKE_VERSION
        msg.addrTo.ip = server_ip
        msg.addrTo.port = server_port
        msg.addrFrom.ip = server_ip
        msg.addrFrom.port = server_port
        return msg


class MockPeerSocket(object):

    def __init__(self):
        self.sent_data = deque()

    def send(self, data):
        self.sent_data.append(data)

    def receive(self) -> bytes:
        return self.sent_data.popleft()
