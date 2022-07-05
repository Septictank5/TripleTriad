from Encryptor import Server
import sys
import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc
import datamanip as dm


class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('chatserver')
        self.setFixedSize(450, 600)
        self.generallayout = qtw.QVBoxLayout()
        self._centralWidget = qtw.QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generallayout)
        self.comms = Server()
        self._create_window()
        self.refreshtimer = qtc.QTimer()
        self.refreshtimer.timeout.connect(self._refresh_windows)
        self.comms.newConnection.connect(self.accept_connection)
        self.datahandler = dm.DataHandler(self.comms.send)
        self.info_to_display = []
        self.status_messages = []
        self.refreshtimer.start(1000)

    def _create_window(self):
        self.windowview = qtw.QTextEdit()
        self.windowview.setReadOnly(True)
        self.windowview.setFixedSize(425, 275)
        self.generallayout.addWidget(self.windowview, 0)

        self.infowindow = qtw.QTextEdit()
        self.infowindow.setReadOnly(True)
        self.infowindow.setFixedSize(425, 275)
        self.generallayout.addWidget(self.infowindow, 1)
        self.infowindow.append('-' * 44 + 'Information' + '-' * 44)

    def _refresh_windows(self):
        self.windowview.clear()
        self.windowview.append('-' * 45 + 'ServerList' + '-' * 45)

        for item in self.datahandler.serverlist:
            self.windowview.append(item[1])

        for item in self.status_messages:
            self.infowindow.append(item)

        self.status_messages.clear()

    def accept_connection(self):
        socket = self.comms.nextPendingConnection()
        self.status_messages.append(f'Connection made with: {self.comms.get_socket_address(socket)}')
        socket.readyRead.connect(lambda: self.recieve_data(socket))
        socket.disconnected.connect(lambda: self.socket_disconnected(socket))
        self.comms.add_socket(socket)

    def recieve_data(self, socket):
        command, data = self.comms.recieve_data(socket)
        if command is None:
            return
        self.status_messages.append(f"{command} received from {self.comms.get_socket_address(socket)}")
        self.status_messages.append(f"{data}")
        if command not in self.datahandler.mydict.keys():
            cipher_data = self.datahandler.turn_to_dict(command, data)
            self.datahandler.pass_through(socket, cipher_data)
            return
        self.datahandler.mydict[command](socket, data)

    def socket_disconnected(self, socket):
        self.datahandler.remove_from_serverlist(socket)
        self.comms.socket_disconnect(socket)


myapp = qtw.QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(myapp.exec())

