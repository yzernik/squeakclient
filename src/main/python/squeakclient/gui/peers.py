import threading

from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtWidgets import QListWidget
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtWidgets import QPushButton


def itemActivated_event(item):
    print(item.text())


class Communicate(QObject):

    peers_updated = pyqtSignal(name='peersUpdated')


class PeersWidget(QWidget):
    def __init__(self, peer_node):
        super(PeersWidget, self).__init__()
        self.peer_node = peer_node

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        peers_list = PeersList(self.peer_node)
        self.layout.addWidget(peers_list)

        add_peer_btn = QPushButton("Add peer")
        add_peer_btn.clicked.connect(self.add_peer)
        self.layout.addWidget(add_peer_btn)

        self.setLayout(self.layout)

    def add_peer(self):
        host, ok = QInputDialog.getText(self, 'New peer input', 'Enter the peer host:')
        print("Trying to connect to host: " + host)

        if ok:
            try:
                self.peer_node.connect_host(host)
            except Exception as e:
                print(e)


class PeersList(QListWidget):

    def __init__(self, peer_node):
        super().__init__()
        self.peer_node = peer_node
        self.lock = threading.Lock()

        self.initUI()

    def initUI(self):

        # self.c = Communicate()
        # self.c.peers_updated.connect(self.addItems)

        # self.setGeometry(300, 300, 290, 150)
        # self.setWindowTitle('Emit signal')
        # self.show()

        self.itemActivated.connect(itemActivated_event)
        self.show()

        self.register_peers_changed_listener()

    def peersUpdatedEvent(self, peers):
        # self.c.peers_updated.emit()
        with self.lock:
            self.set_peers_list_display(peers)

    def set_peers_list_display(self, peers):
        # Remove dropped peers
        peer_names = [peer.address_string for peer in peers]
        for i in range(len(self) - 1, -1, -1):
            item = self.item(i)
            if item.text() not in peer_names:
                self.takeItem(i)

        # Add new peers
        items = self.get_items()
        displayed_peers = [item.text() for item in items]
        for peer in peers:
            item = PeerListItem(peer)
            if item.text() not in displayed_peers:
                self.addItem(item)

    def register_peers_changed_listener(self):
        self.peer_node.listen_peers_changed(self.peersUpdatedEvent)

    def get_items(self):
        ret = []
        for i in range(len(self)):
            item = self.item(i)
            ret.append(item)
        return ret


class PeerListItem(QListWidgetItem):

    def __init__(self, peer):
        super().__init__(peer.address_string)
        self.peer = peer
