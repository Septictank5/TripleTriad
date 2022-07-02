import random


class RewardsHandler:
    def __init__(self):
        self.smv = self.loot_box

    def execute(self, card_data, game_cards):
        self.smv(card_data, game_cards)

    def loot_box(self, card_data, game_cards):
        average = self._get_average_card_level(game_cards)
        templist = []
        for i in range(average - 1, average + 2):
            templist.append(i)

        weights = [25, 25, 35, 15]
        groups = random.choices(templist, weights, k=3)
        card_rewards = []

        for level in groups:
            templist = []
            for card in card_data[level]:
                templist.append(card)

            index = random.randrange(0, len(templist))
            card_rewards.append(templist[index])

        return card_rewards

    def _get_average_card_level(self, cards):
        value = 0
        for card in cards:
            value += card['group']

        return value // len(cards)

    def set_logic(self, logic):
        self.smv = logic

