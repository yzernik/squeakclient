from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtWidgets import QPushButton


class FollowingWidget(QWidget):
    def __init__(self, peer_node):
        super(FollowingWidget, self).__init__()
        self.peer_node = peer_node

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        # peers_list = PeersList(self.peer_node)
        # self.layout.addWidget(peers_list)

        add_follow_btn = QPushButton("Add follow")
        add_follow_btn.clicked.connect(self.add_follow)
        self.layout.addWidget(add_follow_btn)

        self.setLayout(self.layout)

    def add_follow(self):
        address, ok = QInputDialog.getText(self, 'New follow', 'Enter the public address:')
        print("Adding new follow address: " + address)

        if ok:
            # TODO: Add follow to list.
            pass
