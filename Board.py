import PyQt5.QtGui as qtg
import PyQt5.QtCore as qtc
import PyQt5.QtWidgets as qtw
from battlerules import BattleRules, Rules


class Card(qtw.QWidget):
    card_clicked = qtc.pyqtSignal([object])

    def __init__(self, parent, cardid, carddict, isplayers=True, can_move=True, can_click=False):
        super().__init__(parent)
        self.id = cardid
        self.name = carddict['name']
        self.blue_image = qtg.QImage('Data/' + carddict['bluefile'])
        self.red_image = qtg.QImage('Data/' + carddict['redfile'])
        self.powers = {
            'top': carddict['top'],
            'left': carddict['left'],
            'right': carddict['right'],
            'bottom': carddict['bottom']
        }
        self.can_move = can_move
        self.can_click = can_click
        self.in_move = False

        self.isPlayers = isplayers
        self.setFixedSize(125, 158)
        self.animation_timer = qtc.QTimer()
        self.animation_timer.timeout.connect(self.animate)
        self.move_timer = qtc.QTimer()
        self.move_timer.timeout.connect(self.update_pos)
        if self.isPlayers:
            self.iteration = 255
            self.state_machine = self.decrement_iteration
        else:
            self.iteration = 0
            self.state_machine = self.increment_iteration

    def paintEvent(self, event: qtg.QPaintEvent) -> None:
        p = qtg.QPainter(self)
        if self.in_move:
            p.fillRect(self.rect(), qtc.Qt.transparent)
            return
        red_alpha = qtg.QImage(self.red_image.size(), qtg.QImage.Format_Alpha8)
        red_alpha.fill(255 - self.iteration)
        blue_alpha = red_alpha.copy()
        blue_alpha.fill(self.iteration)
        red_image = self.red_image.copy()
        blue_image = self.blue_image.copy()
        red_image.setAlphaChannel(red_alpha)
        blue_image.setAlphaChannel(blue_alpha)
        p.drawImage(self.rect(), red_image)
        p.drawImage(self.rect(), blue_image)

    def mousePressEvent(self, event: qtg.QMouseEvent) -> None:
        if self.can_click:
            self.card_clicked.emit(self)
        else:
            event.ignore()

    def mouseMoveEvent(self, event: qtg.QMouseEvent) -> None:
        if self.id > 4 or not self.can_move:
            return

        image = qtg.QPixmap(self.blue_image)

        mime_data = qtc.QMimeData()

        drag = qtg.QDrag(self)
        drag.setMimeData(mime_data)
        drag.setHotSpot(event.pos())
        drag.setPixmap(image.scaled(125, 158))
        self.in_move = True
        self.update()
        dropaction = drag.exec_(qtc.Qt.MoveAction)

        self.in_move = False
        self.update()

        if dropaction != 0:
            self.can_move = False

    def flip_player_owned(self):
        self.isPlayers = self.isPlayers is False
        self.animation_timer.start(1000//60)

    def animate(self):
        self.state_machine()
        self.update()

    def update_pos(self):
        self.move(qtg.QCursor.pos())
        self.update()

    def increment_iteration(self):
        self.iteration += 10
        if self.iteration >= 255:
            self.iteration = 255
            self.state_machine = self.decrement_iteration
            self.animation_timer.stop()

    def decrement_iteration(self):
        self.iteration -= 10
        if self.iteration <= 0:
            self.iteration = 0
            self.state_machine = self.increment_iteration
            self.animation_timer.stop()

    def sizeHint(self):
        return qtc.QSize(125, 158)

    def set_clickable(self):
        self.can_click = self.can_click is False


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
        event.accept()
        self.cardplaced.emit(self)

    def update_cell_card(self, card):
        card.move(self.pos())
        self.card = card

    def flip_card(self):
        self.card.flip_player_owned()

    def get_neighbors(self):
        return self.neighbor_cells

    def get_card(self):
        return self.card


class BoardHandler(qtc.QObject):
    gameover = qtc.pyqtSignal()

    def __init__(self, game_rules):
        super().__init__()
        self.cells = []

        for i in range(9):
            self.cells.append(Cell(i))
            self.cells[i].cardplaced.connect(self.battle)

        self.rule_handler = BattleRules(self.cells, game_rules)

    def battle(self, cellref: Cell):
        self.rule_handler.execute(cellref)
        self._check_end_game()

    def battle_by_update(self, cellid, card):
        self.cells[cellid].update_cell_card(card)
        self.battle(self.cells[cellid])

    def get_cells(self):
        return self.cells

    def _check_end_game(self):
        filled_cells = 0
        for cell in self.cells:
            if cell.card is not None:
                filled_cells += 1
        if filled_cells == 9:
            self.gameover.emit()



