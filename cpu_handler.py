

class CPUHandler:
    def __init__(self, cells, cards):
        self.cells = cells
        self.cards = cards
        self.opposing_keys = {
            'top': 'bottom',
            'bottom': 'top',
            'left': 'right',
            'right': 'left'
        }

    def execute(self):
        best_choice_per_card = []
        for index, card in enumerate(self.cards):
            templist = []
            for cell in self.cells:
                if cell.card is not None:
                    continue
                power_of_combo = self._get_strength_of_card_cell_combo(card, cell)
                templist.append((power_of_combo, card, cell))
            templist.sort(key=self._sort_mechanism)
            best_choice_per_card.append(templist.pop())
        return self._get_best_combo(best_choice_per_card)

    def _sort_mechanism(self, value):
        return value[0]

    def _get_best_combo(self, best_options):
        best_options.sort(key=self._sort_mechanism)
        best = best_options.pop()
        power, card, cell = best
        return cell, card

    def _get_strength_of_card_cell_combo(self, card, cell):
        opposing_cells = self._get_relevant_cells(cell)
        strength = 0
        for key, other_cell in opposing_cells:
            other_card = other_cell.get_card()
            if other_card is None:
                strength += card.powers[key] - 10
            else:
                if card.powers[key] > other_card.powers[self.opposing_keys[key]] and \
                        card.isPlayers != other_card.isPlayers:
                    strength += 10
        return strength

    def _get_relevant_cells(self, cellref):
        neighbors = cellref.get_neighbors()
        templist = []
        for key, value in neighbors.items():
            if value is not None:
                templist.append((key, self.cells[value]))
        return templist
