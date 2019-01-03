from fbs_runtime.application_context import ApplicationContext, cached_property

from squeakclient.gui.main_window import MainWindow


class AppContext(ApplicationContext):

    def __init__(self, node):
        super().__init__()
        self.node = node

    def run(self):
        stylesheet = self.get_resource('styles.qss')
        self.app.setStyleSheet(open(stylesheet).read())
        self.window.show()
        return self.app.exec_()

    @cached_property
    def window(self):
        return MainWindow(self.node)
