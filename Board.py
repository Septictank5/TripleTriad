import PyQt5.QtGui as qtg
import PyQt5.QtCore as qtc
import PyQt5.QtWidgets as qtw
from battlerules import BattleRules
import random


class Card(qtw.QLabel):
    def __init__(self, cardid, carddict, isplayers=True):
        super().__init__()
        self.id = cardid
        self.name = carddict['name']
        self.bluefile = 'Data/' + carddict['bluefile']
        self.redfile = 'Data/' + carddict['redfile']
        self.powers = {
            'top': carddict['top'],
            'left': carddict['left'],
            'right': carddict['right'],
            'bottom': carddict['bottom']
        }
        self.can_move = True

        self.isPlayers = isplayers
        self.setPixmap(qtg.QPixmap(self.bluefile)) if self.isPlayers is True else self.setPixmap(
            qtg.QPixmap(self.redfile))

        self.setFixedSize(125, 158)
        self.setScaledContents(True)

    def mouseMoveEvent(self, event: qtg.QMouseEvent) -> None:
        if self.id > 4 or not self.can_move:
            return

        mime_data = qtc.QMimeData()

        drag = qtg.QDrag(self)
        drag.setMimeData(mime_data)
        drag.setHotSpot(event.pos())
        drag.setPixmap(self.pixmap().scaled(125, 158))
        self.clear()

        dropaction = drag.exec_(qtc.Qt.MoveAction)
        if dropaction == 0:
            self.reset_pixmap()
        else:
            self.can_move = False

    def flip_player_owned(self):
        self.isPlayers = self.isPlayers is False
        self.setPixmap(qtg.QPixmap(self.bluefile)) if self.isPlayers is True else self.setPixmap(
            qtg.QPixmap(self.redfile))

    def reset_pixmap(self):
        self.setPixmap(qtg.QPixmap(self.bluefile)) if self.isPlayers is True else self.setPixmap(
            qtg.QPixmap(self.redfile))

    def get_pixmap(self):
        return self.pixmap()


class Cell(qtw.QLabel):
    cardplaced = qtc.pyqtSignal([object])

    def __init__(self, cellid):
        super().__init__()
        self.id = cellid
        self.setAcceptDrops(True)
        self.setStyleSheet("border: 4px solid black")
        self.setFixedSize(125, 158)
        mypixmap = qtg.QPixmap()
        mypixmap.load('Data/TTback.jpg')
        self.setPixmap(mypixmap)
        self.setScaledContents(True)
        self.card = None
        self.neighbor_cells = self._set_neighbor_cells()

    def _set_neighbor_cells(self):
        top = None if self.id - 3 < 0 else self.id - 3
        bottom = None if self.id + 3 > 8 else self.id + 3
        left = None if self.id == 0 or self.id == 3 or self.id == 6 else self.id - 1
        right = None if self.id == 2 or self.id == 5 or self.id == 8 else self.id + 1
        return {'top': top, 'bottom': bottom, 'left': left, 'right': right}

    def dragEnterEvent(self, event: qtg.QDragEnterEvent) -> None:
        event.accept()

    def dragMoveEvent(self, event: qtg.QDragMoveEvent) -> None:
        event.accept()

    def dropEvent(self, event: qtg.QDropEvent) -> None:
        event.source().move(self.pos())
        event.setDropAction(qtc.Qt.MoveAction)
        self.card = event.source()
        print(event.source(), self.id)
        self.card.reset_pixmap()
        self.setPixmap(self.card.get_pixmap())
        event.accept()
        self.cardplaced.emit(self)

    def update_cell_card(self, card):
        card.move(self.pos())
        self.card = card
        self.setPixmap(self.card.get_pixmap())

    def flip_card(self):
        self.card.flip_player_owned()

    def get_neighbors(self):
        return self.neighbor_cells

    def get_card(self):
        return self.card


class BoardHandler:
    def __init__(self):
        self.cells = []
        self.rule_handler = BattleRules()

        for i in range(9):
            self.cells.append(Cell(i))
            self.cells[i].cardplaced.connect(self.battle)

    def battle(self, cellref: Cell):
        neighbors = cellref.get_neighbors()
        templist = []
        for key, value in neighbors.items():
            if value is not None:
                if self.cells[value].get_card() is not None:
                    templist.append((key, self.cells[value]))

        self.rule_handler.execute(cellref, templist)

    def battle_by_update(self, cellid, card):
        self.cells[cellid].update_cell_card(card)
        self.battle(self.cells[cellid])

    def set_player(self, player):
        self.player = player

    def get_cells(self):
        return self.cells
