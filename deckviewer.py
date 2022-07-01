import PyQt5.QtCore
import PyQt5.QtCore as qtc
import PyQt5.QtGui as qtg
import PyQt5.QtWidgets as qtw


class CardView(qtw.QLabel):
    leftclicked = qtc.pyqtSignal([object])

    def __init__(self):
        super().__init__()
        font = qtg.QFont()
        font.setPixelSize(48)
        self.setScaledContents(True)
        self.setFixedSize(150, 176)
        self.setFont(font)
        self.setAutoFillBackground(True)
        self.cardpic = qtg.QPixmap()
        self.card_details = {}
        self.load_cancel_pic()
        self.viewonly = True

    def update_pixmap(self, card):
        self.card_details = card
        self.cardpic = qtg.QPixmap()
        self.cardpic.load('Data/' + card['bluefile'])
        self.setPixmap(self.cardpic)

    def load_cancel_pic(self):
        self.cardpic.load('Data/cancel.png')
        self.setPixmap(self.cardpic)

    def mousePressEvent(self, event: qtg.QMouseEvent) -> None:
        if event.button() == qtc.Qt.LeftButton and self.viewonly:
            self.leftclicked.emit(self.card_details)


class HandView(CardView):
    def __init__(self):
        super().__init__()
        self.viewonly = False

    def mousePressEvent(self, event: qtg.QMouseEvent) -> None:
        if event.button() == qtc.Qt.LeftButton:
            self.leftclicked.emit(self)


class MyErrorDialog(qtw.QMessageBox):
    def __init__(self, parent):
        super().__init__(parent)

    def not_enough_cards(self):
        self.setWindowTitle('Error')
        self.setText('Hand Must Contain 5 Cards!')
        self.setIcon(qtw.QMessageBox.Question)
        self.exec()

    def duplicate_card_chosen(self):
        self.setWindowTitle('Error')
        self.setText('No Duplicates Allowed!')
        self.setIcon(qtw.QMessageBox.Question)
        self.exec()


class DeckViewer(qtw.QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowFlag(qtc.Qt.Window)
        self.setWindowTitle('Deck Viewer')
        self.setFixedSize(1200, 800)
        self.setContentsMargins(0, 0, 75, 0)
        self.generallayout = qtw.QGridLayout()
        self.setLayout(self.generallayout)
        self.error_dialog = MyErrorDialog(self)
        self.buttonpanel()
        self.page_number = 0

    def buttonpanel(self):
        self.rightpanel = qtw.QVBoxLayout()
        self.buttonlayout = qtw.QHBoxLayout()
        self.generallayout.addLayout(self.rightpanel, 0, 5, 2, -1)
        self.rightpanel.addLayout(self.buttonlayout, 1)

        self.myfont = qtg.QFont()
        self.myfont.setPixelSize(20)

        self.exit_button = qtw.QPushButton('Exit')
        self.exit_button.setFixedSize(147, 55)
        self.exit_button.setFont(self.myfont)
        self.exit_button.clicked.connect(self.close)
        self.rightpanel.addWidget(self.exit_button, 0)

        self.left_button = qtw.QPushButton('<')
        self.left_button.setFixedSize(70, 55)
        self.left_button.setFont(self.myfont)
        self.left_button.clicked.connect(self._previous_page)
        self.buttonlayout.addWidget(self.left_button, 0)

        self.right_button = qtw.QPushButton('>')
        self.right_button.setFixedSize(70, 55)
        self.right_button.setFont(self.myfont)
        self.right_button.clicked.connect(self._next_page)
        self.buttonlayout.addWidget(self.right_button, 1)

        self.highlighted_card = CardView()
        self.highlighted_card.load_cancel_pic()
        self.rightpanel.addWidget(self.highlighted_card, 2)

        self.rp_padding = qtw.QWidget()
        self.rp_padding.setFixedSize(100, 150)
        self.rightpanel.addWidget(self.rp_padding, 3)

        self.hand = []
        self.bottompanel = qtw.QHBoxLayout()
        self.generallayout.addLayout(self.bottompanel, 3, 0, -1, 3)

        for i in range(5):
            self.hand.append(HandView())
            self.hand[i].leftclicked[object].connect(self._card_move)
            self.bottompanel.addWidget(self.hand[i], i)

    def start_viewer(self, cardlist):
        self.cardlist = cardlist
        self.max_pages = len(cardlist) // 12
        self.labels = []
        self._load_widgets()

    def _load_widgets(self):
        offset = 0
        self.cardviewlayout = qtw.QGridLayout()
        self.generallayout.addLayout(self.cardviewlayout, 0, 0, 2, 3)
        for y in range(3):
            for x in range(4):
                label = CardView()
                label.leftclicked[dict].connect(self._card_selected)
                self.labels.append(label)
                self.cardviewlayout.addWidget(self.labels[offset], y, x)
                offset += 1

        self._display_page()

    def _display_page(self):
        value = 12 if len(self.cardlist[self.page_number * 12:]) > 12 else len(self.cardlist[self.page_number * 12:])
        for index, item in enumerate(self.cardlist[self.page_number * 12:self.page_number * 12 + value]):
            self.labels[index].update_pixmap(item)

        if value < 12:
            for i in range(12 - value):
                self.labels[value + i].load_cancel_pic()

    def _next_page(self):
        self.page_number += 1 if self.page_number != self.max_pages else 0
        self._display_page()

    def _previous_page(self):
        self.page_number -= 1 if self.page_number != 0 else 0
        self._display_page()

    def _card_selected(self, card):
        self.highlighted_card.update_pixmap(card)
        self.selected_card = card

    def _card_move(self, handview):
        for label in self.hand:
            if label.card_details == self.selected_card:
                self.error_dialog.duplicate_card_chosen()
                return
        handview.update_pixmap(self.selected_card)

    def get_hand(self):
        templist = []
        for label in self.hand:
            if label.card_details != {}:
                templist.append(label.card_details)

        return templist

    def set_hand(self, cardlist):
        for index, label in enumerate(self.hand):
            label.update_pixmap(cardlist[index])

    def closeEvent(self, event: qtg.QCloseEvent) -> None:
        templist = []
        for label in self.hand:
            if label.card_details != {}:
                templist.append(label.card_details)

        if len(templist) == 5:
            self.finished.emit(1)
            event.accept()
        else:
            self.error_dialog.not_enough_cards()
            event.ignore()
