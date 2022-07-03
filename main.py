import PyQt5.QtWidgets as qtw
from LobbyUI import LobbyWindow
from cardsinterface import CardHandler
from deckviewer import DeckViewer
from GameUI import GameWindow
import sys
from Client_Comms import ClientUI


class TripleTriad:
    def __init__(self):
        self.comms = ClientUI()
        self.cardsmanager = CardHandler()
        self.comms.readyRead.connect(self.receive_data)
        self.main_menu = self.comms.get_window()
        self.deck_viewer = DeckViewer(self.main_menu)
        self.lobby_screen = LobbyWindow(self.main_menu)
        self._connect_signals()
        self.main_menu.show()
        self.startup()

    def startup(self):
        if self.cardsmanager.get_name() is None:
            playername = ''
            while playername == '':
                playername = self.comms.prompt_create_profile()[0]
            self.cardsmanager.create_starter_deck(playername)

    def shutdown(self):
        self.cardsmanager.save_data()
        sys.exit()

    def _connect_signals(self):
        self.main_menu.quit_clicked().connect(self.lobby_screen.show)
        self.main_menu.deck_viewer_clicked().connect(self.start_cardviewer)
        self.lobby_screen.view_deck_clicked().connect(self.start_cardviewer)
        self.lobby_screen.start_clicked().connect(self.game_start)
        self.lobby_screen.ready_clicked().connect(self.ready_up)
        self.lobby_screen.unready_clicked().connect(self.unready)
        self.deck_viewer.finished.connect(self._get_hand)

    def start_cardviewer(self):
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

        if command == 'Move Update':
            cells = self.game.get_cells()
            for cell in cells:
                cell.setAcceptDrops(True)
            cellid, cardid = data
            self.game.do_battle(cellid, cardid)

        elif command == 'Connection Established As Host':
            self.host = True
            self.initialize_settings()
            self.comms.host_success()

        elif command == 'Connection Established As Client':
            self.host = False
            self.initialize_settings()

        elif command == 'Ready':
            self.opponent_cards = data
            self.lobby_screen.update_other_ready()

        elif command == 'Not Ready':
            self.lobby_screen.update_other_not_ready()

        elif command == 'Game Start':
            self.opponent_cards = data
            self.create_game_window()
            cells = self.game.get_cells()
            for cell in cells:
                cell.setAcceptDrops(False)
        else:
            self.comms.handle_data(command, data)

    def game_start(self):
        self.create_game_window()
        self.comms.send_game_starting(self.mycards)

    def create_game_window(self):
        self.mycards = self.cardsmanager.get_hand()
        self.cardsmanager.set_game_cards(self.mycards + self.opponent_cards)
        reward_logic_index = self.lobby_screen.get_rr_box_index()
        self.cardsmanager.set_reward_logic(reward_logic_index)
        self.lobby_screen.hide()
        self.game = GameWindow(self.main_menu, self.cardsmanager)
        self.game.get_confirmed_rewards().connect(self.handle_gameover)
        self.game.show()
        cells = self.game.get_cells()

        for cell in cells:
            cell.cardplaced.connect(self.card_placed)

    def card_placed(self, cell):
        cells = self.game.get_cells()
        for eachcell in cells:
            eachcell.setAcceptDrops(False)
        self.comms.card_place_notify(cell)

    def ready_up(self):
        self.lobby_screen.update_self_ready()
        self.comms.player_ready(self.cardsmanager.get_hand())

    def unready(self):
        self.lobby_screen.update_self_not_ready()
        self.comms.player_not_ready()

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

    def handle_gameover(self, cards: list, winstatus: str):
        if len(cards) > 0:
            if winstatus == 'WINNER':
                self.cardsmanager.add_cards_to_playerdata(cards)
            if winstatus == 'LOSER':
                self.cardsmanager.remove_cards_from_playerdata(cards)
        self.game.close()
        self.flip_host()
        self.initialize_settings()

    def flip_host(self):
        self.host = self.host is False

    # noinspection PyUnusedLocal
    def _get_hand(self, value):
        self.cards_for_game = self.deck_viewer.get_hand()


def main():
    myapp = qtw.QApplication(sys.argv)
    game = TripleTriad()
    sys.exit(myapp.exec())


if __name__ == '__main__':
    main()
