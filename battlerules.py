class BattleRules:
    def __init__(self, cells, rulesets: list):
        self.no_special_rules = True
        self.cells = cells

        self.rulesets = {
            'Same': 0,
            'Plus': 0,
            'Difference': 0,
            'Combo': 0,
            'Sudden Death': 0,
            'Same Wall': 0
        }

        self.update_rules(rulesets)

        self.opposing_keys = {
            'top': 'bottom',
            'bottom': 'top',
            'left': 'right',
            'right': 'left'
        }

    def execute(self, played_cell, opposing_cells: list):
        played_card = played_cell.get_card()
        for key, cell in opposing_cells:
            other_card = cell.get_card()
            if played_card.isPlayers == other_card.isPlayers:
                continue
            if played_card.powers[key] > other_card.powers[self.opposing_keys[key]]:
                cell.flip_card()

    def standard_calc(self, cardpower1, cardpower2):
        return cardpower1 > cardpower2

    def update_rules(self, rules: list):
        for index, value in enumerate(rules):
            self.rulesets[index] = value
