from rewards import RewardsHandler
from playerdata import Player
from filehandler import FileHandler


class CardHandler:
    def __init__(self):
        self.rewards = RewardsHandler()
        self.player = Player()
        self.filehandler = FileHandler()
        self.get_last_profile()

    def load_profile(self, name):
        hand, cardlist = self.filehandler.load_profile(name)
        self.player.set_from_profile(name, cardlist, hand)

    def create_starter_deck(self, name):
        self.filehandler.profile_created(name)
        cardlist = self.filehandler.create_starter_deck()
        self.player.create_starter_deck(name, cardlist)
        hand = self.player.get_hand()
        self.filehandler.save_profile(name, cardlist, hand)

    def get_last_profile(self):
        name, cardlist, hand = self.filehandler.get_last_profile()
        self.player.set_from_profile(name, cardlist, hand)

    def get_hand(self):
        return self.player.get_hand()

    def get_name(self):
        return self.player.get_name()

    def get_cards(self):
        return self.player.get_cards()

    def save_data(self):
        name, cardlist, hand = self.player.get_profile_data()
        self.filehandler.save_profile(name, cardlist, hand)

    def get_rewards(self, card_data, game_cards):
        return self.rewards.execute(card_data, game_cards)

    def set_reward_logic(self, logic):
        self.rewards.set_logic(logic)






