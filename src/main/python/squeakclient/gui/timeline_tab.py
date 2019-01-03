import threading

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QListWidget
from PyQt5.QtWidgets import QListWidgetItem


class TimelineWidget(QWidget):
    def __init__(self, client_node):
        super(TimelineWidget, self).__init__()
        self.client_node = client_node

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        squeak_list = SqueakList(self.client_node)
        self.layout.addWidget(squeak_list)

        make_squeak_btn = QPushButton("Make squeak")
        make_squeak_btn.clicked.connect(self.make_squeak)
        self.layout.addWidget(make_squeak_btn)

        self.setLayout(self.layout)

    def make_squeak(self):
        content, ok = MakeSqueakDialog.getSqueakInputs()

        if ok:
            try:
                self.client_node.make_squeak(content)
            except Exception as e:
                self.show_make_squeak_failed_popup(str(e))

    def show_make_squeak_failed_popup(self, msg):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Make Squeak Error")
        msg_box.setText("Failed to make squeak.")
        msg_box.setDetailedText(msg)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()


class MakeSqueakDialog(QDialog):
    def __init__(self, parent=None):
        super(MakeSqueakDialog, self).__init__(parent)

        layout = QVBoxLayout(self)

        self.setWindowTitle("Make Squeak")

        # nice widget for editing the text content
        self.content = QTextEdit(self)
        layout.addWidget(self.content)

        self.is_reply_to = QCheckBox(self)
        layout.addWidget(self.is_reply_to)

        self.reply_to = QLineEdit(self)
        self.reply_to.setEnabled(False)
        layout.addWidget(self.reply_to)

        # OK and Cancel buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # get current content and reply-to hash from the dialog
    def squeak_inputs(self):
        return self.content.toPlainText()

    # static method to create the dialog and return (content, accepted)
    @staticmethod
    def getSqueakInputs(parent=None):
        dialog = MakeSqueakDialog(parent)
        result = dialog.exec_()
        content = dialog.squeak_inputs()
        return (content, result == QDialog.Accepted)


class SqueakList(QListWidget):

    def __init__(self, client_node):
        super().__init__()
        self.client_node = client_node
        self.lock = threading.Lock()

        self.initUI()

    def initUI(self):
        self.show()

        self.register_squeaks_changed_listener()

    def squeaksUpdatedEvent(self, squeaks):
        # self.c.squeaks_updated.emit()
        with self.lock:
            self.set_squeaks_list_display(squeaks)

    def set_squeaks_list_display(self, squeaks):
        # Remove dropped squeaks
        squeak_names = [squeak.address_string for squeak in squeaks]
        for i in range(len(self) - 1, -1, -1):
            item = self.item(i)
            if item.text() not in squeak_names:
                self.takeItem(i)

        # Add new squeaks
        items = self.get_items()
        displayed_squeaks = [item.text() for item in items]
        for squeak in squeaks:
            item = SqueakListItem(squeak)
            if item.text() not in displayed_squeaks:
                self.addItem(item)

    def register_squeaks_changed_listener(self):
        # TODO
        pass

    def get_items(self):
        ret = []
        for i in range(len(self)):
            item = self.item(i)
            ret.append(item)
        return ret


class SqueakListItem(QListWidgetItem):

    def __init__(self, squeak):
        super().__init__(squeak.address_string)
        self.squeak = squeak
