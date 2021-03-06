import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg
import PyQt5.QtCore as qtc
from GameUI import GameWindow


class TTCheckBox(qtw.QCheckBox):
    state_change = qtc.pyqtSignal([str])

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.clicked.connect(self.better_state_change)

    def better_state_change(self):
        self.state_change.emit(self.text())


class LobbyWindow(qtw.QMainWindow):
    def __init__(self, parent):
        super().__init__(parent)

        self.setWindowTitle('Lobby')
        self.setFixedSize(1200, 900)
        self.generallayout = qtw.QGridLayout()
        self._centralWidget = qtw.QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generallayout)

        self.player = 0
        self.other_player = 0
        self._create_view()

    def _create_view(self):
        self.rightpanel = qtw.QVBoxLayout()
        self._add_buttons()
        self._add_rules()
        self._add_restrictions()
        self._add_risk_reward()
        self.flip_settings_enabled()
        self._add_labels()
        self.panelpad = qtw.QWidget()
        self.panelpad.setFixedSize(250, 600)
        self.rightpanel.addWidget(self.panelpad, 20)

        self.chatwindow = qtw.QTextEdit()
        self.chatwindow.setReadOnly(True)
        self.chatwindow.setFixedSize(900, 800)
        self.chatline = qtw.QLineEdit()
        self.chatline.setFixedSize(900, 40)

        self.generallayout.addWidget(self.chatwindow, 0, 0)
        self.generallayout.addWidget(self.chatline, 1, 0)
        self.generallayout.addLayout(self.rightpanel, 0, 3)

    def _add_buttons(self):
        self.unready_button = qtw.QPushButton('UnReady')
        self.unready_button.setFixedSize(250, 50)
        self.unready_button.hide()
        self.start_button = qtw.QPushButton('Start')
        self.start_button.setFixedSize(250, 50)
        self.start_button.setDisabled(True)
        self.ready_button = qtw.QPushButton('Ready')
        self.ready_button.setFixedSize(250, 50)
        self.rightpanel.addWidget(self.ready_button, 0)
        self.rightpanel.addWidget(self.start_button, 0)
        self.rightpanel.addWidget(self.unready_button, 0)
        self.unready_button.hide()
        self.start_button.hide()
        self.ready_button.hide()

        self.view_deck_button = qtw.QPushButton('View Deck')
        self.view_deck_button.setFixedSize(250, 50)
        self.rightpanel.addWidget(self.view_deck_button, 1)

        self.exit_button = qtw.QPushButton('Exit')
        self.exit_button.setFixedSize(250, 50)
        self.rightpanel.addWidget(self.exit_button, 2)

    def _add_rules(self):
        rules = ['Same', 'Plus', 'Difference', 'Combo', 'Sudden Death', 'Same Wall']
        self.checkboxes = []
        for index, rule in enumerate(rules):
            self.checkboxes.append(TTCheckBox(rule))
        self.rulesbox = qtw.QGroupBox('Rules')
        self.ruleslayout = qtw.QGridLayout()
        self.rulesbox.setLayout(self.ruleslayout)
        self.ruleslayout.addWidget(self.checkboxes[0], 0, 0)
        self.ruleslayout.addWidget(self.checkboxes[1], 0, 1)
        self.ruleslayout.addWidget(self.checkboxes[2], 1, 0)
        self.ruleslayout.addWidget(self.checkboxes[3], 1, 1)
        self.ruleslayout.addWidget(self.checkboxes[4], 2, 0)
        self.ruleslayout.addWidget(self.checkboxes[5], 2, 1)
        self.rightpanel.addWidget(self.rulesbox, 3)

    def _add_restrictions(self):
        self.restrictions_layout = qtw.QHBoxLayout()
        self.restrictions_label = qtw.QLabel('Restrictions:')
        self.restrictions_label.setFixedSize(100, 20)
        self.restrictions_box = qtw.QComboBox()
        self.restrictions_box.setFixedSize(150, 20)
        self.restrictions_box.addItems(['None', 'Group 1', 'Group 2', 'Group 3', 'Group 4', 'Group 5', 'Group 6',
                                        'Group 7', 'Group 8', 'Group 9', 'Group 10', 'Random Cards'])
        self.restrictions_layout.addWidget(self.restrictions_label, 0)
        self.restrictions_layout.addWidget(self.restrictions_box, 1)
        self.rightpanel.addLayout(self.restrictions_layout, 4)

    def _add_risk_reward(self):
        self.rewards_layout = qtw.QHBoxLayout()
        self.rr_label = qtw.QLabel('Risk & Reward:')
        self.rr_label.setFixedSize(100, 20)
        self.rr_box = qtw.QComboBox()
        self.rr_box.setFixedSize(150, 20)
        self.rr_box.addItems(['W:Loot Box - L: None', 'W:Choose 1 - L: Lose 1', 'W:Takes All - L:Loses All'])
        self.rewards_layout.addWidget(self.rr_label, 0)
        self.rewards_layout.addWidget(self.rr_box, 1)
        self.rightpanel.addLayout(self.rewards_layout, 5)

    def _add_labels(self):
        labelfont = qtg.QFont()
        labelfont.setPixelSize(24)
        self.ready_label = qtw.QLabel()
        self.ready_label.setText('P2 Not Ready')
        self.ready_label.setFont(labelfont)
        self.rightpanel.addWidget(self.ready_label, 7)

    def get_rr_box_update(self):
        return self.rr_box.activated

    def get_rules_checkboxes(self):
        return self.checkboxes

    def get_rules_checkboxes_state(self):
        templist = []
        for box in self.checkboxes:
            templist.append(box.isChecked())
        return templist

    def start_clicked(self):
        return self.start_button.clicked

    def ready_clicked(self):
        return self.ready_button.clicked

    def unready_clicked(self):
        return self.unready_button.clicked

    def view_deck_clicked(self):
        return self.view_deck_button.clicked

    def exit_clicked(self):
        return self.exit_button.clicked

    def set_turn(self, mybool=True):
        self.is_my_turn = mybool

    def update_self_ready(self):
        self.ready_label.setText(f'P2 Ready')
        self.ready_button.hide()
        self.unready_button.show()

    def update_self_not_ready(self):
        self.ready_label.setText(f'P2 Not ready')
        self.ready_button.show()
        self.unready_button.hide()

    def update_other_ready(self):
        self.ready_label.setText(f'P2 Ready')
        self.start_button.setEnabled(True)

    def update_other_not_ready(self):
        self.ready_label.setText(f'P2 Not Ready')
        self.start_button.setDisabled(True)

    def host_setup(self):
        self.player = 1
        self.other_player = 2
        self.ready_button.hide()
        self.unready_button.hide()
        self.start_button.show()
        self.flip_settings_enabled()

    def client_setup(self):
        self.player = 2
        self.other_player = 1
        self.start_button.hide()
        self.flip_settings_enabled()

    def flip_settings_enabled(self):
        value = self.rr_box.isEnabled() is False
        self.rr_box.setEnabled(value)
        self.rulesbox.setEnabled(value)
        self.restrictions_box.setEnabled(value)
