import random

from rewards import RewardsHandler
from playerdata import Player
from filehandler import FileHandler


class CardHandler:
    def __init__(self):
        self.rewards = RewardsHandler()
        self.player = Player()
        self.filehandler = FileHandler()
        self.get_last_profile()
        self.computer_hand = None
        self.game_cards = None

    def load_profile(self, name):
        hand, cardlist = self.filehandler.load_profile(name)
        self.player.set_from_profile(name, cardlist, hand)

    def create_starter_deck(self, name):
        self.filehandler.profile_created(name)
        cardlist = self.filehandler.create_starter_deck()
        self.player.create_starter_deck(name, cardlist)
        hand = self.player.get_hand()
        self.filehandler.save_profile(cardlist, hand)

    def get_last_profile(self):
        name, cardlist, hand = self.filehandler.get_last_profile()
        self.player.set_from_profile(name, cardlist, hand)

    def get_cards_for_cpu_game(self):
        playerhand = self.player.get_hand()
        average_level = self._get_average_card_level(playerhand)
        computer_hand = self.filehandler.gen_hand_of_level(average_level)
        self.set_game_cards(playerhand + computer_hand)
        return playerhand + computer_hand

    def set_computer_cards(self, cards):
        self.computer_hand = cards

    def remove_from_computer(self, card):
        self.computer_hand.remove(card)

    def _get_average_card_level(self, cards):
        value = 0
        for card in cards:
            value += card['group']

        return value // len(cards)

    def get_hand(self):
        return self.player.get_hand()

    def get_name(self):
        return self.player.get_name()

    def get_cards(self):
        return self.player.get_cards()

    def set_hand(self, cards):
        self.player.set_hand(cards)

    def save_data(self):
        name, cardlist, hand = self.player.get_profile_data()
        self.filehandler.save_profile(cardlist, hand)

    def get_rewards(self):
        card_data = self.filehandler.get_card_data()
        return self.rewards.execute(card_data, self.game_cards)

    def set_reward_logic(self, index):
        self.rewards.set_logic(index)

    def get_logic(self):
        return self.rewards.get_logic()

    def set_game_cards(self, game_cards):
        self.game_cards = game_cards

    def get_game_cards(self):
        return self.game_cards

    def get_profile_list(self):
        return self.filehandler.get_profile_list()

    def get_random_card(self):
        value = 0
        for card in self.game_cards:
            value += card['group']
        average = value // 10 + random.randint(1, 2)
        if average > 10:
            average = 10
        return self.filehandler.get_random_card_from_group(average)

    def add_cards_to_playerdata(self, cards: list):
        playercards = self.player.get_cards()
        for card in cards:
            if card not in playercards:
                playercards.append(card)
        playerhand = self.player.get_hand()
        cards_sorted = self.filehandler.update_and_save(playercards, playerhand)
        self.player.set_cardlist(cards_sorted)

    def remove_cards_from_playerdata(self, cards: list):
        playercards = self.player.get_cards()
        playerhand = self.player.get_hand()
        for index, card in enumerate(cards):
            if card in playercards:
                playercards.remove(card)
            if card in playerhand:
                playerhand.remove(card)
        self.player.fix_hand()
        cards_sorted = self.filehandler.update_and_save(playercards, playerhand)
        self.player.set_cardlist(cards_sorted)

    def get_computer_hand(self):
        return self.computer_hand



