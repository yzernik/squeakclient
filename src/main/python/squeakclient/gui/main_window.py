from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QTabWidget

from squeakclient.gui.channels import ChannelsWidget
from squeakclient.gui.following import FollowingWidget
from squeakclient.gui.peers import PeersWidget
from squeakclient.gui.keys import SingingKeyWidget
from squeakclient.gui.timeline_tab import TimelineWidget


class MainWindow(QWidget):
    def __init__(self, node):
        super().__init__()
        self.node = node

        self.setup_window()

    def setup_window(self):
        # Create layout
        self.layout = QVBoxLayout()

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tabs.resize(300,200)

        # Add timeline tab
        timeline_tab = TimelineWidget(self.node)
        self.tabs.addTab(timeline_tab, "Timeline")

        # Add following tab
        following_tab = FollowingWidget(self.node)
        self.tabs.addTab(following_tab, "Following")

        # Add Signing tab
        signing_tab = QWidget()
        signing_tab.layout = QVBoxLayout()
        key_widget = SingingKeyWidget(self.node)
        signing_tab.layout.addWidget(key_widget)
        signing_tab.setLayout(signing_tab.layout)
        self.tabs.addTab(signing_tab, "Signing")

        # Add peers tab
        peers_tab = PeersWidget(self.node)
        self.tabs.addTab(peers_tab, "Peers")

        # Add funds tab
        funds_tab = QWidget()
        funds_tab.layout = QVBoxLayout()
        funds_tab.setLayout(funds_tab.layout)
        self.tabs.addTab(funds_tab, "Funds")

        # Add channels tab
        channels_tab = ChannelsWidget(self.node)
        self.tabs.addTab(channels_tab, "Channels")

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        self.show()
