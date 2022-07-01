import PyQt5.QtGui as qtg
import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc
from Board import BoardHandler, Card


class GameWindow(qtw.QMainWindow):
    def __init__(self, parent, game_cards):
        super().__init__(parent)
        self.setWindowTitle('Triple Triad')
        self.setFixedSize(1100, 900)
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
        self.board = BoardHandler()
        self.game_view(game_cards)
        self.show()

    def game_view(self, cards: list):
        cells = self.board.get_cells()
        self.cardobjects = []
        for index, carddetails in enumerate(cards):
            if index < 5:
                self.cardobjects.append(Card(index, carddetails))
            else:
                self.cardobjects.append(Card(index, carddetails, False))

        self.cellslayout = qtw.QGridLayout()
        self.cellslayout.setHorizontalSpacing(2)
        self.cellslayout.setVerticalSpacing(3)

        for index, cell in enumerate(cells):
            self.cellslayout.addWidget(cell, index // 3, index % 3)

        self.generallayout.addLayout(self.cellslayout, 2, 1)

        self.framelayout = qtw.QVBoxLayout()
        for index, card in enumerate(self.cardobjects[:5]):
            self.framelayout.addWidget(card, index)
        self.framelayout2 = qtw.QVBoxLayout()
        for index, card in enumerate(self.cardobjects[5:]):
            self.framelayout2.addWidget(card, index)
        self.generallayout.addLayout(self.framelayout, 0, 0, 5, 1)
        self.generallayout.addLayout(self.framelayout2, 0, 4, 5, 1)

        self.frames = []

        for index, item in enumerate(self.frames):
            if index < 5:
                self.framelayout.addWidget(item, index)
            else:
                self.framelayout2.addWidget(item, index % 5)

    def get_cells(self):
        return self.board.get_cells()

    def do_battle(self, cellid, cardid):
        for card in self.cardobjects:
            if card.id == cardid + 5:
                self.board.battle_by_update(cellid, card)
                break


