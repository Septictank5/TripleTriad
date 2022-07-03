import random


class RewardsHandler:
    def __init__(self):
        self.smv = self.loot_box
        self.logic_index = 0
        self.logic = [self.loot_box, self.win_1_lose_1, self.win_all_lose_all]

    def execute(self, card_data, game_cards):
        # noinspection PyArgumentList
        return self.logic[self.logic_index](card_data, game_cards)

    def loot_box(self, card_data: list, game_cards: list):
        average = self._get_average_card_level(game_cards)
        templist = []
        for i in range(average - 1, average + 3):
            if i > 10:
                break
            templist.append(i)

        weights = [25, 25, 35, 15]
        while len(templist) < len(weights):
            del weights[-1]
        groups = random.choices(templist, weights, k=3)
        card_rewards = []

        for level in groups:
            templist = []
            for card in card_data[level]:
                templist.append(card)

            index = random.randrange(0, len(templist))
            card_rewards.append(templist[index])

        return card_rewards, None

    def win_1_lose_1(self, card_data: list, game_cards: list):
        win_loss_cards = game_cards[:5]
        return win_loss_cards, win_loss_cards

    def win_all_lose_all(self, card_data: list, game_cards: list):
        win_loss_cards = game_cards[:5]
        return win_loss_cards, win_loss_cards

    def _get_average_card_level(self, cards):
        value = 0
        for card in cards:
            value += card['group']

        return value // len(cards)

    def set_logic(self, index):
        self.logic_index = index
        self.smv = self.logic[index]

    def get_logic(self):
        return self.logic_index
