import threading

from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QListWidget
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtWidgets import QMessageBox

from squeak.core.signing import CSqueakAddress


class FollowingWidget(QWidget):
    def __init__(self, client_node):
        super(FollowingWidget, self).__init__()
        self.client_node = client_node

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        follow_list = FollowingList(self.client_node)
        self.layout.addWidget(follow_list)

        add_follow_btn = QPushButton("Add follow")
        add_follow_btn.clicked.connect(self.add_follow)
        self.layout.addWidget(add_follow_btn)

        self.setLayout(self.layout)

    def add_follow(self):
        address, ok = QInputDialog.getText(self, 'New follow', 'Enter the public address:')
        print("Adding new follow address: " + address)

        if ok:
            try:
                follow = CSqueakAddress(address)
                self.client_node.add_follow(follow)
            except Exception as e:
                self.show_add_follow_failed_popup(str(e))

    def show_add_follow_failed_popup(self, msg):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Add Follow Error")
        msg_box.setText("Failed to add follow.")
        msg_box.setDetailedText(msg)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()


class FollowingList(QListWidget):

    def __init__(self, client_node):
        super().__init__()
        self.client_node = client_node
        self.lock = threading.Lock()

        self.initUI()

    def initUI(self):
        self.show()

        self.register_follows_changed_listener()

    def followsUpdatedEvent(self, follows):
        with self.lock:
            self.set_follows_list_display(follows)

    def set_follows_list_display(self, follows):
        # Remove current
        for i in range(len(self) - 1, -1, -1):
            item = self.item(i)
            self.takeItem(i)

        # Add new
        for follow in follows:
            item = FollowListItem(follow)
            self.addItem(item)

    def register_follows_changed_listener(self):
        self.client_node.listen_follows_changed(self.followsUpdatedEvent)

    def get_items(self):
        ret = []
        for i in range(len(self)):
            item = self.item(i)
            ret.append(item)
        return ret


class FollowListItem(QListWidgetItem):

    def __init__(self, follow):
        super().__init__(str(follow))
        self.follow = follow
