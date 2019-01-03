import threading

from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QFormLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QLineEdit

from squeak.core.signing import CSigningKey


class SingingKeyWidget(QWidget):
    def __init__(self, client_node):
        super(SingingKeyWidget, self).__init__()
        self.client_node = client_node
        self.lock = threading.Lock()

        self.initUI()

        self.register_key_changed_listener()

    def initUI(self):
        layout = QFormLayout()

        self.btn1 = QPushButton("Import private key")
        self.btn1.clicked.connect(self.get_signing_key)
        layout.addRow(QLabel("Set private key:"), self.btn1)

        self.btn2 = QPushButton("Generate private key")
        self.btn2.clicked.connect(self.generate_signing_key)
        layout.addRow(QLabel("Generate private key:"), self.btn2)

        self.b = QLineEdit()
        self.b.setReadOnly(True)
        self.b.setText("No private key imported.")
        layout.addRow(QLabel("Public address:"), self.b)

        self.setLayout(layout)

    def get_signing_key(self):
        text, ok = QInputDialog.getText(self, 'Private Key Input', 'Enter your private key in WIF format:')

        if ok:
            try:
                signing_key = CSigningKey(text)
                self.client_node.set_signing_key(signing_key)
            except Exception as e:
                self.show_invalid_key_popup(str(e))

    def generate_signing_key(self):
        try:
            self.client_node.generate_signing_key()
        except Exception as e:
            self.show_invalid_key_popup(str(e))

    def show_invalid_key_popup(self, msg):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Load Private Key Error")
        msg_box.setText("Failed to load private key.")
        msg_box.setDetailedText(msg)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def keyUpdatedEvent(self, address):
        with self.lock:
            self.set_address_display(address)

    def set_address_display(self, address):
        self.b.setText(str(address))

    def register_key_changed_listener(self):
        self.client_node.listen_key_changed(self.keyUpdatedEvent)
