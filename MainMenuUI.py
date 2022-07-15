import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg
import PyQt5.QtCore as qtc
import sys


class MyInputDialog(qtw.QInputDialog):
    def __init__(self):
        super().__init__()
        self.setFixedSize(400, 400)
        self.generallayout = qtw.QGridLayout()
        self.setLayout(self.generallayout)

    def prompt_server_list(self, serverlist):
        self.setWindowTitle('ServerList')
        self.setOkButtonText('Connect')
        return self.getItem(self, 'Server List', 'Choose a Server:', serverlist)

    def prompt_profile_list(self, serverlist):
        self.setWindowTitle('ServerList')
        self.setOkButtonText('Connect')
        return self.getItem(self, 'Server List', 'Choose a Server:', serverlist)

    def prompt_host_game(self):
        self.setWindowTitle('Host Game')
        self.setOkButtonText('Host Game')
        return self.getText(self, 'Host Game', 'Game Name:', text='MyGame')

    def prompt_create_profile(self):
        self.setWindowTitle('Profile Creation')
        self.setOkButtonText('Create')
        return self.getText(self, 'Profile Creator', 'Enter Profile Name:')


class MyErrorDialog(qtw.QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Error')
        self.myfont = qtg.QFont()
        self.myfont.setPixelSize(18)
        self.setFont(self.myfont)
        self.button = qtw.QPushButton('OK')
        self.setDefaultButton(self.button)

    def error_no_servers(self):
        self.setWindowTitle('Error')
        self.setText('No Servers Available')
        self.setIcon(qtw.QMessageBox.Question)
        self.button.setText('OK')
        self.exec()

    def server_not_online(self):
        self.setWindowTitle('Error')
        self.setText('Server Offline')
        self.setIcon(qtw.QMessageBox.Question)
        self.button.setText('OK')
        self.exec()


class MyInfoDialog(qtw.QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.generallayout = qtw.QGridLayout()
        self.setLayout(self.generallayout)
        self.textlabel = qtw.QLabel()
        self.setFixedSize(200, 150)
        font = qtg.QFont()
        font.setPixelSize(24)
        self.textlabel.setFixedSize(180, 80)
        self.textlabel.setFont(font)
        self.textlabel.setWordWrap(True)
        self.padding = qtw.QWidget()
        self.padding.setFixedSize(100, 50)
        self.cancel_button = qtw.QPushButton('Cancel')
        self.cancel_button.setFixedSize(70, 40)
        self.cancel_button.clicked.connect(self.reject)
        self.generallayout.addWidget(self.textlabel, 0, 0)
        self.generallayout.addWidget(self.padding, 1, 0)
        self.generallayout.addWidget(self.cancel_button, 1, 1)

    def awaiting_player(self):
        self.setWindowTitle('Hosting Game')
        self.textlabel.setText('Awaiting Player To Connect...')
        self.exec()

    def success(self):
        self.done(1)

    def host_cancel_clicked(self):
        return self.cancel_button.clicked


class ProfileDialog(qtw.QDialog):
    profile_chosen = qtc.pyqtSignal([str])
    profile_created = qtc.pyqtSignal([str])

    def __init__(self, profiles, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Profile')
        self.setFixedSize(300, 150)
        self.mainlayout = qtw.QHBoxLayout()
        self.setLayout(self.mainlayout)
        self.create_screen(profiles)

    def create_screen(self, profiles):
        self.create_layout = qtw.QVBoxLayout()
        self.load_layout = qtw.QVBoxLayout()

        self.create_button = qtw.QPushButton('Create')
        self.create_button.setFixedSize(100, 100)
        self.create_button.clicked.connect(self.create_clicked)
        self.textedit = qtw.QLineEdit('New Profile')
        self.textedit.setFixedSize(100, 20)
        self.create_layout.addWidget(self.textedit, 0)
        self.create_layout.addWidget(self.create_button, 1)

        self.load_button = qtw.QPushButton('Load')
        self.load_button.setFixedSize(100, 100)
        self.load_button.clicked.connect(self.load_clicked)
        self.profile_box = qtw.QComboBox()
        self.profile_box.addItems(profiles)
        self.profile_box.setFixedSize(100, 20)
        self.load_layout.addWidget(self.profile_box, 0)
        self.load_layout.addWidget(self.load_button, 1)

        self.mainlayout.addLayout(self.create_layout, 0)
        self.mainlayout.addLayout(self.load_layout, 1)

    def create_clicked(self):
        text = self.textedit.text()
        if text != '':
            self.profile_created.emit(text)
            self.close()

    def load_clicked(self):
        self.profile_chosen.emit(self.profile_box.currentText())
        self.close()


class MainMenu(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Triple Triad')
        self.setFixedSize(320, 700)
        self.generallayout = qtw.QVBoxLayout()
        self._centralWidget = qtw.QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generallayout)
        self.input_dialog = MyInputDialog()
        self.error_dialog = MyErrorDialog()
        self.info_dialog = MyInfoDialog(self)
        self.add_buttons()

    def add_buttons(self):
        self.profile_button = qtw.QPushButton('Profile')
        self.profile_button.setFixedSize(300, 100)
        self.generallayout.addWidget(self.profile_button, 0)

        self.vs_computer_button = qtw.QPushButton('Vs. Computer')
        self.vs_computer_button.setFixedSize(300, 100)
        self.generallayout.addWidget(self.vs_computer_button, 0)

        self.host_game_button = qtw.QPushButton('Create Online Game')
        self.host_game_button.setFixedSize(300, 100)
        self.generallayout.addWidget(self.host_game_button, 1)

        self.server_list_button = qtw.QPushButton('Join Online Game')
        self.server_list_button.setFixedSize(300, 100)
        self.generallayout.addWidget(self.server_list_button, 2)

        self.deck_viewer_button = qtw.QPushButton('View Cards')
        self.deck_viewer_button.setFixedSize(300, 100)
        self.generallayout.addWidget(self.deck_viewer_button, 3)

        self.quit_button = qtw.QPushButton('Exit')
        self.quit_button.setFixedSize(300, 100)
        self.generallayout.addWidget(self.quit_button, 4)

    def get_input_dialog(self):
        return self.input_dialog

    def get_error_dialog(self):
        return self.error_dialog

    def get_info_dialog(self):
        return self.info_dialog

    def host_clicked(self):
        return self.host_game_button.clicked

    def join_clicked(self):
        return self.server_list_button.clicked

    def quit_clicked(self):
        return self.quit_button.clicked

    def profile_clicked(self):
        return self.profile_button.clicked

    def deck_viewer_clicked(self):
        return self.deck_viewer_button.clicked

    def vs_computer_clicked(self):
        return self.vs_computer_button.clicked

    def show_profile_screen(self, profile_list):
        return ProfileDialog(profile_list, self)
