import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc
from LobbyUI import LobbyWindow, TTCheckBox
from cardsinterface import CardHandler
from deckviewer import DeckViewer
from GameUI import GameWindow
import sys
from Client_Comms import ClientUI
from cpu_handler import CPUHandler


class VSComputerDialog(qtw.QDialog):
    confirmed = qtc.pyqtSignal([list])

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle('VS Computer Rules')
        self.main_layout = qtw.QVBoxLayout()
        self.main_layout.setContentsMargins(50, 0, 50, 0)
        self.setFixedSize(300, 300)
        self.setLayout(self.main_layout)
        self.create_view()

    def create_view(self):
        rules = ['Same', 'Plus', 'Difference', 'Combo', 'Sudden Death', 'Same Wall']
        self.checkboxes = []
        for index, rule in enumerate(rules):
            self.checkboxes.append(TTCheckBox(rule))
        self.rulesbox = qtw.QGroupBox('Rules')
        self.rulesbox.setFixedSize(200, 200)
        self.ruleslayout = qtw.QGridLayout()
        self.rulesbox.setLayout(self.ruleslayout)
        self.ruleslayout.addWidget(self.checkboxes[0], 0, 0)
        self.ruleslayout.addWidget(self.checkboxes[1], 0, 1)
        self.ruleslayout.addWidget(self.checkboxes[2], 1, 0)
        self.ruleslayout.addWidget(self.checkboxes[3], 1, 1)
        self.ruleslayout.addWidget(self.checkboxes[4], 2, 0)
        self.ruleslayout.addWidget(self.checkboxes[5], 2, 1)
        self.main_layout.addWidget(self.rulesbox, 0)

        button_layout = qtw.QHBoxLayout()
        #  button_layout.setContentsMargins(1, 0, 1, 0)
        self.ok_button = qtw.QPushButton('Play')
        self.ok_button.setFixedSize(100, 40)
        self.ok_button.clicked.connect(self.dialog_confirmed)
        button_layout.addWidget(self.ok_button, 0)

        self.cancel_button = qtw.QPushButton('CANCEL')
        self.cancel_button.setFixedSize(100, 40)
        button_layout.addWidget(self.cancel_button)

        self.main_layout.addLayout(button_layout, 1)

    def dialog_confirmed(self):
        self.confirmed.emit(self.get_checkbox_states())
        self.close()

    def get_checkbox_states(self):
        templist = []
        for box in self.checkboxes:
            templist.append(box.isChecked())
        return templist


class TripleTriad:
    def __init__(self):
        self.computer_game = False
        self.comms = ClientUI()
        self.cardsmanager = CardHandler()
        self.comms.readyRead.connect(self.receive_data)
        self.main_menu = self.comms.get_window()
        self.deck_viewer = DeckViewer(self.main_menu)
        self.lobby_screen = LobbyWindow(self.main_menu)
        self._main_menu_signals()
        self._lobby_screen_signals()
        self._deck_viewer_signals()
        self.main_menu.show()
        self.startup()
        self.handle_command = {
            'Move Update': self._move_update,
            'Connection Established As Host': self._host_game,
            'Connection Established As Client': self._client_game,
            'Ready': self._ready,
            'Not Ready': self._not_ready,
            'Game Start': self._game_start,
            'Reward Update': self._reward_update,
            'Card Lost': self._card_lost,
            'Rules Update': self._rules_update
        }

    def startup(self):
        if self.cardsmanager.get_name() is None:
            playername = ''
            while playername == '':
                playername = self.comms.prompt_create_profile()[0]
            self.cardsmanager.create_starter_deck(playername)

    def _shutdown(self):
        self.cardsmanager.save_data()
        sys.exit()

    def _main_menu_signals(self):
        self.main_menu.quit_clicked().connect(self._shutdown)
        self.main_menu.deck_viewer_clicked().connect(self._start_cardviewer)
        self.main_menu.profile_clicked().connect(self._profile)
        self.main_menu.vs_computer_clicked().connect(self.cpu_rules)

    def _lobby_screen_signals(self):
        self.lobby_screen.view_deck_clicked().connect(self._start_cardviewer)
        self.lobby_screen.start_clicked().connect(self._start_game)
        self.lobby_screen.ready_clicked().connect(self._send_ready)
        self.lobby_screen.unready_clicked().connect(self._send_not_ready)
        self.lobby_screen.get_rr_box_update().connect(self._update_reward_setting)

        for box in self.lobby_screen.get_rules_checkboxes():
            box.state_change.connect(self._notify_rule_update)

    def _deck_viewer_signals(self):
        self.deck_viewer.finished.connect(self._get_hand)

    def _profile(self):
        profiles = self.cardsmanager.get_profile_list()
        dialog = self.main_menu.show_profile_screen(profiles)
        dialog.profile_created.connect(self.cardsmanager.create_starter_deck)
        dialog.profile_chosen.connect(self.cardsmanager.load_profile)
        dialog.exec()

    def _start_cardviewer(self):
        self.deck_viewer.set_hand(self.cardsmanager.get_hand())
        self.deck_viewer.start_viewer(self.cardsmanager.get_cards())
        self.deck_viewer.exec()

    def receive_data(self, testdata=None):
        if testdata is None:
            command, data = self.comms.receive_data()
        else:
            command, data = testdata

        if command is None:
            return

        if command in self.handle_command.keys():
            self.handle_command[command](data)
        else:
            self.comms.handle_data(command, data)

    def _host_game(self, data):
        self.host = True
        self.initialize_settings()
        self.comms.host_success()

    def _client_game(self, data):
        self.host = False
        self.initialize_settings()
        self.lobby_screen.flip_settings_enabled()

    def _ready(self, data):
        self.opponent_cards = data
        self.lobby_screen.update_other_ready()

    def _not_ready(self, data):
        self.lobby_screen.update_other_not_ready()

    def _move_update(self, data):
        cells = self.game.get_cells()
        for cell in cells:
            cell.setAcceptDrops(True)
        cellid, cardid = data
        self.game.do_battle(cellid, cardid)

    def _card_lost(self, data):
        self.game.winscreen.card_loss_update(data)

    def _reward_update(self, data):
        self._update_reward_setting(data)

    def _game_start(self, data):
        self.opponent_cards = data
        self.create_game_window()
        cells = self.game.get_cells()
        for cell in cells:
            cell.setAcceptDrops(False)

    def _rules_update(self, rulename):
        for box in self.lobby_screen.get_rules_checkboxes():
            if box.text() == rulename:
                box.setChecked(box.isChecked() is False)

    def _notify_rule_update(self, rulename):
        print('notify rule updated')
        self.comms.send_data('Rules Update', rulename)

    def _start_game(self):
        self.create_game_window()
        self.comms.send_data('Game Start', self.mycards)

    def create_game_window(self):
        self.mycards = self.cardsmanager.get_hand()
        self.cardsmanager.set_game_cards(self.mycards + self.opponent_cards)
        self.lobby_screen.hide()
        game_rules = self.lobby_screen.get_rules_checkboxes_state()
        self.game = GameWindow(self.main_menu, self.cardsmanager, game_rules)
        self.game.get_confirmed_rewards().connect(self.handle_gameover)
        self.game.show()
        cells = self.game.get_cells()

        for cell in cells:
            cell.cardplaced.connect(self.card_placed)

    def _update_reward_setting(self, index):
        self.cardsmanager.set_reward_logic(index)
        if self.host:
            self.comms.send_data('Reward Update', index)
        else:
            self.lobby_screen.rr_box.setCurrentIndex(index)

    def card_placed(self, cell):
        cells = self.game.get_cells()
        for eachcell in cells:
            eachcell.setAcceptDrops(False)
        self.comms.send_data('Move Update', [cell.id, cell.card.id])

    def _send_ready(self):
        self.lobby_screen.update_self_ready()
        self.comms.send_data('Ready', self.cardsmanager.get_hand())

    def _send_not_ready(self):
        self.lobby_screen.update_self_not_ready()
        self.comms.send_data('Not Ready')

    def initialize_settings(self):
        if self.host:
            self.lobby_screen.set_turn()
            self.lobby_screen.host_setup()
            self.lobby_screen.update_other_not_ready()
            self.is_host = True
            self.lobby_screen.show()

        else:
            self.lobby_screen.set_turn(False)
            self.lobby_screen.client_setup()
            self.lobby_screen.update_self_not_ready()
            self.is_host = False
            self.lobby_screen.show()

    def handle_gameover(self, cards: list, winstatus: str, logic_index: int):
        if logic_index == 1:
            self.comms.send_data('Card Lost', cards)
        if len(cards) > 0:
            if winstatus == 'WINNER':
                self.cardsmanager.add_cards_to_playerdata(cards)
            if winstatus == 'LOSER':
                self.cardsmanager.remove_cards_from_playerdata(cards)
        self.game.close()
        if not self.computer_game:
            self.flip_host()
            self.initialize_settings()
        else:
            self.computer_game = False

    def cpu_rules(self):
        dialog = VSComputerDialog(self.main_menu)
        dialog.confirmed.connect(self.play_computer)
        dialog.open()

    def play_computer(self, game_rules):
        self.game_on = True
        self.computer_game = True
        self.cards_for_game = self.cardsmanager.get_cards_for_cpu_game()
        self.game = GameWindow(self.main_menu, self.cardsmanager, game_rules)
        self.game.gameover.connect(self._end_cpu_game)
        self.cardsmanager.set_computer_cards(self.game.get_cards()[5:])
        self.game.get_confirmed_rewards().connect(self.handle_gameover)
        self.game.show()
        cells = self.game.get_cells()

        for cell in cells:
            cell.cardplaced.connect(self.card_placed_cpu_game)

    def card_placed_cpu_game(self, cell):
        cells = self.game.get_cells()
        for eachcell in cells:
            eachcell.setAcceptDrops(False)
        if self.game_on:
            self.handle_cpu_turn()

    def handle_cpu_turn(self):
        cells = self.game.get_cells()
        cards = self.cardsmanager.get_computer_hand()
        cpu = CPUHandler(cells, cards)
        cell, card = cpu.execute()
        self.game.do_battle(cell.id, card.id - 5)
        self.cardsmanager.remove_from_computer(card)
        for cell in cells:
            cell.setAcceptDrops(True)

    def _end_cpu_game(self):
        self.game_on = False

    def flip_host(self):
        self.host = self.host is False

    # noinspection PyUnusedLocal
    def _get_hand(self, value):
        self.cards_for_game = self.deck_viewer.get_hand()
        self.cardsmanager.set_game_cards(self.cards_for_game)
        self.cardsmanager.set_hand(self.cards_for_game)


def main():
    myapp = qtw.QApplication(sys.argv)
    game = TripleTriad()
    sys.exit(myapp.exec())


if __name__ == '__main__':
    main()
