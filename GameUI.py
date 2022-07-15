import PyQt5.QtGui as qtg
import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc
from PyQt5.QtMultimedia import *
from Board import BoardHandler, Card
from cardsinterface import CardHandler


class Playlist:
    def __init__(self):
        self.playlist = QMediaPlaylist()
        self.playlist.addMedia(QMediaContent(qtc.QUrl.fromLocalFile('Audio/TT.mp3')))
        self.playlist.setPlaybackMode(QMediaPlaylist.Loop)
        self.player = QMediaPlayer()
        self.volume = 50
        self.player.setVolume(self.volume)
        self.player.setPlaylist(self.playlist)
        self.player.play()

    def switch(self):
        self.player.stop()
        self.playlist.clear()
        self.player.setMedia(QMediaContent(qtc.QUrl.fromLocalFile('Audio/fanfare.mp3')))
        self.player.play()

    def end(self):
        self.timer = qtc.QTimer()
        self.timer.timeout.connect(self.fadeout)
        self.timer.start(1000//20)

    def fadeout(self):
        self.volume -= 1
        self.player.setVolume(self.volume)
        if self.volume == 0:
            self.player.stop()
            self.timer.stop()


class WinScreen(qtw.QDialog):
    rewards_confirmed = qtc.pyqtSignal([list, str, int])

    def __init__(self, parent, cardmanager: CardHandler):
        super().__init__(parent)
        self.setWindowTitle('Card Rewards')
        self.setFixedSize(650, 300)
        self.generallayout = qtw.QVBoxLayout()
        self.setLayout(self.generallayout)
        self.cardmanager = cardmanager
        self.card_chosen = False
        self._label_setup()

    def _label_setup(self):
        self.winloss_text = qtw.QLabel()
        self.winloss_text.setAlignment(qtc.Qt.AlignCenter)
        font = qtg.QFont()
        font.setPixelSize(24)
        self.winloss_text.setFont(font)
        self.generallayout.addWidget(self.winloss_text, 0)
        self.generallayout.setAlignment(self.winloss_text, qtc.Qt.AlignCenter)

    def setup_reward_screen(self):
        self.logic_index = self.cardmanager.get_logic()
        self.cardlayout = qtw.QHBoxLayout()
        self.generallayout.addLayout(self.cardlayout, 1)
        self.cardobjects = []
        if self.winstatus == 'LOSER':
            if self.logic_index == 1:
                self.awaiting_card()
                return
            else:
                self.winloss_text.setText(f"You Lose!!!\n-Cards Lost-")
            self.cards = self.cardmanager.get_rewards()[1]
        elif self.winstatus == 'WINNER':
            self.winloss_text.setText(f"You Win!!!\n-Cards Won-")
            self.cards = self.cardmanager.get_rewards()[0]
        else:
            self.winloss_text.setText(f"Tie Game!!!\nTake a random card!")
            self.cards = [self.cardmanager.get_random_card()]

        if not self.cards:
            self.winloss_text.setText(f"You Lose!!!\n Luckily for you, no cards lost!")
            self.rewards = []
            return

        for index, card in enumerate(self.cards):
            if self.logic_index == 1:
                self.cardobjects.append(Card(self, index, card, can_move=False, can_click=True))
                self.cardobjects[index].card_clicked.connect(self.display_card)
            else:
                self.cardobjects.append(Card(self, index, card, can_move=False))
                if card == self.cards[-1]:
                    self.rewards = self.cards
            self.cardlayout.addWidget(self.cardobjects[index])

    def awaiting_card(self):
        self.winloss_text.setText(f"You have lost!\nAwaiting other player to choose a card...")

    def display_card(self, card_choice):
        self.card_chosen = True
        for index, card in enumerate(self.cardobjects):
            if card == card_choice:
                self.rewards = [self.cards[index]]
            else:
                card.close()

    def get_card_click_signals(self):
        templist = []
        for card in self.cards:
            templist.append(card.card_clicked)
        return templist

    def set_winstatus(self, winstatus):
        self.winstatus = winstatus
        self.setup_reward_screen()

    def get_winstatus(self):
        return self.winstatus

    def card_loss_update(self, cards):
        self.winloss_text.setText(f"Opponent Chose the following Card(s)!\n -Card(s) Lost-")
        self.rewards = cards
        for card in cards:
            cardobject = Card(self, 0, card, can_move=False)
            self.cardlayout.addWidget(cardobject)
        self.card_chosen = True

    def closeEvent(self, event: qtg.QCloseEvent) -> None:
        if self.card_chosen is False and self.logic_index == 1:
            event.ignore()
            return

        self.rewards_confirmed.emit(self.rewards, self.winstatus, self.logic_index)


class GameWindow(qtw.QMainWindow):
    gameover = qtc.pyqtSignal()

    def __init__(self, parent, cardmanager: CardHandler, game_rules: list):
        super().__init__(parent)
        self.playlist = Playlist()
        self.gameover.connect(self.playlist.switch)
        self.setWindowTitle('Triple Triad')
        self.setFixedSize(1100, 900)
        self.cardmanager = cardmanager
        self.winscreen = WinScreen(self, cardmanager)
        self.winscreen.rewards_confirmed.connect(self.close)
        cellgridpic = qtg.QImage('Data/game_background.jpg')
        cellsbrush = qtg.QBrush(cellgridpic.scaled(1100, 900))
        blackbrush = qtg.QBrush(qtc.Qt.black)
        palette = qtg.QPalette(blackbrush, qtc.Qt.black, blackbrush, blackbrush, blackbrush, blackbrush,
                               blackbrush, blackbrush, cellsbrush)
        self.setPalette(palette)
        self.generallayout = qtw.QGridLayout()
        self._centralWidget = qtw.QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generallayout)
        self.board = BoardHandler(game_rules)
        self.board.gameover.connect(self.is_winner)
        self.game_view()

    def game_view(self):
        self.cellobjects = self.board.get_cells()
        self.cardobjects = []
        for index, carddetails in enumerate(self.cardmanager.get_game_cards()):
            if index < 5:
                self.cardobjects.append(Card(self, index, carddetails))
            else:
                self.cardobjects.append(Card(self, index, carddetails, False))

        self.cellslayout = qtw.QGridLayout()
        self.cellslayout.setHorizontalSpacing(2)
        self.cellslayout.setVerticalSpacing(3)

        for index, cell in enumerate(self.cellobjects):
            self.cellslayout.addWidget(cell, index // 3, index % 3)

        self.generallayout.addLayout(self.cellslayout, 2, 1)

        self.p1handlayout = qtw.QVBoxLayout()
        for index, card in enumerate(self.cardobjects[:5]):
            self.p1handlayout.addWidget(card, index)
        self.p2handlayout = qtw.QVBoxLayout()
        for index, card in enumerate(self.cardobjects[5:]):
            self.p2handlayout.addWidget(card, index)
        self.generallayout.addLayout(self.p1handlayout, 0, 0, 5, 1)
        self.generallayout.addLayout(self.p2handlayout, 0, 4, 5, 1)

        self.frames = []

        for index, item in enumerate(self.frames):
            if index < 5:
                self.p1handlayout.addWidget(item, index)
            else:
                self.p2handlayout.addWidget(item, index % 5)

    def get_cells(self):
        return self.board.get_cells()

    def get_cards(self):
        return self.cardobjects

    def do_battle(self, cellid, cardid):
        for card in self.cardobjects:
            if card.id == cardid + 5:
                self.board.battle_by_update(cellid, card)
                break

    def get_confirmed_rewards(self):
        return self.winscreen.rewards_confirmed

    def closeEvent(self, event: qtg.QCloseEvent) -> None:
        self.playlist.end()

    def is_winner(self):
        self.gameover.emit()
        value = 0
        for card in self.cardobjects:
            if card.isPlayers:
                value += 1
        if value > 5:
            self.winscreen.set_winstatus('WINNER')
        elif value < 5:
            self.winscreen.set_winstatus('LOSER')
        else:
            self.winscreen.set_winstatus('TIED')

        self.winscreen.show()
