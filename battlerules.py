from enum import Enum

class Rules(Enum):
    SAME = 'Same'
    PLUS = 'Plus'
    DIFFERENCE = 'Difference'
    COMBO = 'Combo'
    SUDDEN_DEATH = 'Sudden Death'
    SAME_WALL = 'Same Wall'

    @classmethod
    def iterate(cls):
        for member in cls:
            yield member


class BattleRules:
    def __init__(self, cells, rulesets: list):
        self.no_special_rules = True
        self.cells = cells

        self.rulesets = {}

        self.update_rules(rulesets)

        self.opposing_keys = {
            'top': 'bottom',
            'bottom': 'top',
            'left': 'right',
            'right': 'left'
        }

    def execute(self, played_cell):
        opposing_cells = self._get_relevant_cells(played_cell)
        played_card = played_cell.get_card()

        if self.rulesets[Rules.SAME]:
            self._calc_same(played_card, opposing_cells)
        if self.rulesets[Rules.PLUS]:
            self._calc_plus(played_card, opposing_cells)
        for key, cell in opposing_cells:
            other_card = cell.get_card()
            print(played_card.isPlayers, other_card.isPlayers)
            print(self._standard_calc(played_card, other_card, key))
            if played_card.isPlayers == other_card.isPlayers:
                continue
            if self._standard_calc(played_card, other_card, key):
                cell.flip_card()

    def _calc_same(self, played_card, opposing_cells):
        templist = []
        for key, cell in opposing_cells:
            other_card = cell.get_card()
            if self._compare_same(played_card, other_card, key):
                templist.append(cell)

        if len(templist) > 1:
            enemy_only = []
            for cell in templist:
                card = cell.get_card()
                if played_card.isPlayers != card.isPlayers:
                    enemy_only.append(cell)
                    card.flip_player_owned()

            if self.rulesets[Rules.COMBO]:
                self._combo_calc(enemy_only)

    def _calc_plus(self, played_card, opposing_cells):
        templist = []
        plus_cells = []
        for key, cell in opposing_cells:
            other_card = cell.get_card()
            for cellid, value in templist:
                if self._add_powers(played_card, other_card, key) == value:
                    if not self._compare_owners(played_card, other_card) or \
                            not self._compare_owners(played_card, self.cells[cellid].get_card()):
                        plus_cells.append([self.cells[cellid], cell])

            templist.append([cell.id, played_card.powers[key] + other_card.powers[self.opposing_keys[key]]])

        for celllist in plus_cells:
            card1 = celllist[0].get_card()
            if not self._compare_owners(played_card, card1):
                card1.flip_player_owned()
            card2 = celllist[1].get_card()
            if not self._compare_owners(played_card, card2):
                card2.flip_player_owned()
            if self.rulesets[Rules.COMBO]:
                self._combo_calc(celllist)

    def _get_relevant_cells(self, cellref):
        neighbors = cellref.get_neighbors()
        templist = []
        for key, value in neighbors.items():
            if value is not None:
                if self.cells[value].get_card() is not None:
                    templist.append((key, self.cells[value]))
        return templist

    def _standard_calc(self, card1, card2, key):
        return card1.powers[key] > card2.powers[self.opposing_keys[key]]

    def _compare_same(self, card1, card2, key):
        return card1.powers[key] == card2.powers[self.opposing_keys[key]]

    def _compare_owners(self, card1, card2):
        return card1.isPlayers == card2.isPlayers

    def _add_powers(self, card1, card2, key):
        return card1.powers[key] + card2.powers[self.opposing_keys[key]]

    def _combo_calc(self, celllist):
        templist = []
        for cell in celllist:
            combo_card = cell.get_card()
            opposing_cells = self._get_relevant_cells(cell)
            for key, opposing_cell in opposing_cells:
                other_card = opposing_cell.get_card()
                if combo_card.isPlayers == other_card.isPlayers:
                    continue
                if self._standard_calc(combo_card, other_card, key):
                    other_card.flip_player_owned()
                    templist.append(opposing_cell)

        if len(templist) > 0:
            self._combo_calc(templist)

    def update_rules(self, rules: list):
        gen = Rules.iterate()
        for value in rules:
            self.rulesets[next(gen)] = value

