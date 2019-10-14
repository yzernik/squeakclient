import threading

from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QFormLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QLineEdit

from squeak.core.signing import CSqueakAddress


class ChannelsWidget(QWidget):
    def __init__(self, client_node):
        super(ChannelsWidget, self).__init__()
        self.client_node = client_node
        self.lock = threading.Lock()

        self.initUI()

    def initUI(self):
        layout = QFormLayout()

        self.btn2 = QPushButton("Get wallet balance")
        self.btn2.clicked.connect(self.get_wallet_balance)
        layout.addRow(QLabel("Get wallet balance:"), self.btn2)

        self.b = QLineEdit()
        self.b.setReadOnly(True)
        self.b.setText("No balance reported.")
        layout.addRow(QLabel("Wallet balance:"), self.b)

        self.setLayout(layout)

    def get_wallet_balance(self):
        try:
            balance = self.client_node.get_wallet_balance()
            self.set_balance_display(balance)
        except Exception as e:
            print("Get wallet balance failed: " + str(e))
            self.show_invalid_key_popup(str(e))

    def show_invalid_key_popup(self, msg):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Get wallet balance error")
        msg_box.setText("Failed to get wallet balance.")
        msg_box.setDetailedText(msg)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def set_balance_display(self, address):
        self.b.setText(str(address))
